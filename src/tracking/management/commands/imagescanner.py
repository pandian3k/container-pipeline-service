from django.core.management.base import BaseCommand  # CommandError
import logging
import json
from django.utils import timezone
from django.conf import settings

from tracking.models import ContainerImage, Package, RepoInfo
from tracking.lib import get_navr_from_pkg_name
from vendors import beanstalkc

logger = logging.getLogger('cccp')


def populate_packages(container):
    """Populate RPM packages installed data from container image"""
    logger.debug('Populating packages for image: %s' % container)
    output = container.run('rpm -qa')
    packages = []
    for line in output.splitlines():
        if not line:
            continue
        name, arch, version, release = get_navr_from_pkg_name(line)
        p, created = Package.objects.get_or_create(
            name=name, version=version, release=release, arch=arch)
        packages.append(p)
    container.packages.add(*packages)


def populate_upstreams(container):
    """Populate enabled repos data from container image"""
    logger.debug('Populating upstream data for image: %s' % container)
    output = container.run(
        'python -c "import yum, json; yb = yum.YumBase(); '
        'print json.dumps([(r.id, r.mirrorlist, r.baseurl) '
        'for r in yb.repos.listEnabled()])"')
    data = json.loads(output.splitlines()[-1])
    urls = set()
    for item in data:
        urls.add(item[1])
        for url in item[2]:
            urls.add(url)
    output = container.run(
        'python -c "import yum, json; yb = yum.YumBase(); '
        'print json.dumps(yb.conf.yumvar)"')
    data = json.loads(output.splitlines()[-1])
    basearch = data['basearch']
    releasever = data['releasever']
    infra = data['infra']
    repoinfo, created = RepoInfo.objects.get_or_create(
        baseurls=json.dumps(list(urls)), defaults={
            'releasever': releasever, 'basearch': basearch,
            'infra': infra
        })
    container.repoinfo = repoinfo
    container.save()


def scan_image(image):
    """Scan the given container image"""
    image.pull()
    populate_packages(image)
    populate_upstreams(image)
    image.scanned = True
    image.last_scanned = timezone.now()
    image.save()
    image.remove()


class Command(BaseCommand):
    help = 'Scan container images'
    args = '[onetime <image_name1> <image_name2> ...]'

    def handle(self, *args, **options):
        logger.info('Scanning not already scanned images')
        filters = {}
        if args:
            if args[0] != 'onetime':
                filters['name__in'] = args
            filters['scanned'] = False
        for image in ContainerImage.objects.filter(**filters):
            try:
                scan_image(image)
            except Exception as e:
                logger.error('Image scan error for %s: %s' % (image, e),
                             exc_info=True)
        logger.info('Scanned not already scanned images')

        if not args:
            logger.info('Image scanner running...')
            bs = beanstalkc.Connection(host=settings.BEANSTALK_SERVER)
            bs.watch('tracking')
            while True:
                try:
                    job = bs.reserve()
                    job_details = json.loads(job.body)
                    logger.debug(
                        'Scanning image post delivery for %s' % job_details)
                    image_name = '{}/{}:{}'.format(
                        job_details['appid'], job_details['jobid'],
                        job_details['desired_tag'])
                    image = ContainerImage.objects.get(name=image_name)
                    scan_image(image)
                except Exception as e:
                    logger.error('Image scan error: %s' % e, exc_info=True)
