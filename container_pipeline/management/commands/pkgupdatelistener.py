from django.core.management.base import BaseCommand

import fedmsg
import logging
import sys

from container_pipeline.models.tracking import Package

logger = logging.getLogger('tracking')


class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info('Listening for package updates...')
        for name, endpoint, topic, msg in fedmsg.tail_messages():
            try:
                if topic.endswith('package.modified') or \
                        topic.endswith('package.removed') or \
                        topic.endswith('package.added'):
                    pkg = msg['msg']['package']
                    repoinfo_id = msg['msg'].get('upstream')
                    for package in Package.objects.filter(
                            name=pkg['name'], arch=pkg['arch']):
                        if package.version != pkg['version'] or \
                                package.release != pkg['release']:
                            logger.info('Package changed: %s %s'
                                        % (pkg, package))
                            images_qs = package.images.all()
                            if repoinfo_id is not None:
                                images_qs = images_qs.filter(
                                    repoinfo__id=repoinfo_id)
                            images_qs.update(to_build=True)
                            logger.info('Images marked for build: %s'
                                        % images_qs)
            except Exception as e:
                logger.critical('pkgupdatelistener errored out: %s' % e,
                                exc_info=True)
                sys.exit(1)
