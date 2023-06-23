# -*- coding: utf-8 -*-
import requests
import json
from django.conf import settings
from django.apps import apps as django_apps
from django.contrib.contenttypes.models import ContentType

from django.core.management.base import BaseCommand

from eucs_platform import visao
from projects.models import *


def create_dataset(auth_header, name, keyword, description, category_id):
    endpoint = settings.VISAO_URL
    record = {'name': name,
              'active': True,
              'keyWord': keyword,
              'description': description,
              'bigArea': {'id': 12, 'name': 'Informação e Comunicação'},
              'categories': [
                  {
                      "cod": {"category": {"id": category_id}},
                      "ordemApresentacao": 1,
                  }
                ]
              }
    response = requests.post(f'{endpoint}/app/api/group-layers', json=record,
                             timeout=20, verify=False, headers=auth_header)
    if response.status_code == 201:
        record = json.loads(response.content)
        return record['id']
    else:
        try:
            record = json.loads(response.content)
            message = record['detail']
        except:
            message = response.status_code
        raise Exception('%s' % message)


def delete_dataset(auth_header, dataset_id):
    tot_excluidos = 0
    endpoint = settings.VISAO_URL
    query = {'groupId.equals': dataset_id}
    response = requests.get(f'{endpoint}/app/api/layers', params=query, verify=False,
                            headers=auth_header)
    if response.status_code == 200:
        result = json.loads(response.text)
        if len(result) > 0:
            for item in result:
                item_id = item['id']
                response = requests.delete(f'{endpoint}/app/api/layers/{item_id}', verify=False, headers=auth_header)
                if response.status_code == 200:
                    tot_excluidos += 1
                else:
                    print('API error %d' % response.status_code)

    response = requests.delete(f'{endpoint}/app/api/group-layers/{dataset_id}', verify=False, headers=auth_header)
    if response.status_code == 200:
        print(f'Group layer deleted. {tot_excluidos} layers deleted')
    else:
        print('Error deleting group layer: %d' % response.status_code)
    return


class Command(BaseCommand):
    label = 'Populate Visão with Project info'

    # topics: include also all topics associated
    # delete_all: delete all dataset projects before insert new ones
    def populate_projects(self, topics=False, delete_all=False):
        # Remove todos os projetos existentes
        auth_header = visao.authenticate()
        if delete_all:
            tot_projects = visao.delete_all(auth_header)
            print(f'Projects removed: {tot_projects}')
        tot_projects = 0
        if topics:
            dataset_id = None
        else:
            dataset_id = settings.VISAO_LAYER

        for project in Project.objects.filter(approved=True):
            visao.save_project(project, auth_header, dataset_id)
            tot_projects += 1
        print(f'Projects added: {tot_projects}')

    def populate_topics(self):
        auth_header = visao.authenticate()
        domain = settings.DOMAIN
        ctype = ContentType.objects.get_for_model(Topic)
        count_topics = 0
        count_projects = 0
        for topic in Topic.objects.all():
            if topic.external_url is None and topic.project_set.count() > 0:
                dataset_id = create_dataset(auth_header, topic.topic,
                                            f"Tema {topic.id}",
                                            f'{domain}/projects?topic={topic.topic}&id={topic.id}',
                                            settings.VISAO_CATEGORY)
                count_topics += 1
                if dataset_id:
                    topic.external_url = f'grupCategory={settings.VISAO_GROUP}&e=f&l={dataset_id}'
                    topic.save()
                    for project in topic.project_set.all():
                        visao.save_project(project, auth_header, dataset_id)
                        count_projects += 1
        print(f'Topics included {count_topics}')
        print(f'Projects included {count_projects}')

    # Cria os datasets dos tópicos - Deleted because we are not using the Civis Translation structure
    '''
    def populate_topics_localized(self):
        auth_header = visao.authenticate()
        ctype = ContentType.objects.get_for_model(Topic)
        count_topics = 0
        count_projects = 0
        domain = settings.DOMAIN
        for record in Translation.objects.filter(language=settings.LANGUAGE_CODE, content_type_id=ctype.id):
            topic = record.content_object
            if topic.external_url is None and topic.project_set.count() > 0:
                dataset_id = create_dataset(auth_header, record.text,
                                            f"Tema {topic.id}",
                                            f'{domain}/projects?topic={record.text}&id={topic.id}',
                                            settings.VISAO_CATEGORY)

                count_topics += 1
                if dataset_id:
                    topic.external_url = f'grupCategory={settings.VISAO_GROUP}&e=f&l={dataset_id}'
                    topic.save()
                    for project in topic.project_set.all():
                        visao.save_project(project, auth_header, dataset_id)
                        count_projects += 1
        print(f'Topics included {count_topics}')
        print(f'Projects included {count_projects}')
    '''

    def add_arguments(self, parser):
        parser.add_argument('-a', '--auth', action="store_true", help='Test authentication')
        parser.add_argument('-n', '--new', action="store_true", help='Create new Map')
        parser.add_argument('-m', '--info', type=int, help='Get Map parameters')
        parser.add_argument('-t', '--topics', action="store_true", help='Create Topics')
        parser.add_argument('-p', '--projects', action="store_true", help='Create/Update Projects')
        parser.add_argument('-d', '--delete', type=int, help='Delete Group Layer')

    def handle(self, *args, **options):
        if options['auth']:
            auth_header = visao.authenticate()
            print('Auth ok')

        elif options['new']:
            auth_header = visao.authenticate()
            endpoint = settings.VISAO_URL
            record = {"name": settings.SITE_NAME, "type": "LAYER", "level": 0 }
            response = requests.post(f'{endpoint}/app/api/categories', json=record, headers=auth_header)
            if response.status_code == 201:
                category_id = response.json()['id']
                print(f'VISAO_CATEGORY={category_id}')
            else:
                print('Error inserting new category')
                exit(-1)

            record = {
                "about": "Civis T2",
                "tipoMapa": "NACIONAL",
                "geonetworkGroupId": 5608,
                "categories": [
                    {"cod": {"category": {"id": category_id}}, "ordemApresentacao": 0}
                ],
            }
            response = requests.post(f'{endpoint}/app/api/grup-categories', json=record, headers=auth_header)
            if response.status_code == 201:
                group_id = response.json()['id']
                print(f'VISAO_GROUP={group_id}')
            else:
                print('Error inserting new group category')
                exit(-1)

            dataset_id = create_dataset(auth_header, 'Projects', settings.SITE_NAME, 'Projects', category_id)
            print(f'VISAO_LAYER={dataset_id}')

        elif options['info']:
            auth_header = visao.authenticate()
            endpoint = settings.VISAO_URL
            query = {'id.equals': options['info']}
            response = requests.get(f'{endpoint}/app/api/grup-categories', params=query, headers=auth_header)
            if response.status_code == 200:
                print('VISAO_GROUP=%s' % options['info'])
            else:
                print('Invalid Group ID')
                exit(-1)

            category_id = None
            record = response.json()
            print('USERID: ',record[0]['owner']['id'])
            query = {'ownerId.equals': record[0]['owner']['id']}
            response = requests.get(f'{endpoint}/app/api/categories', params=query, headers=auth_header)
            if response.status_code == 200:
                groups = response.json()
                if len(groups) > 0:
                    category_id = groups[0]['id']

            if category_id:
                print(f'VISAO_CATEGORY={category_id}')
            else:
                print('Category ID not found')
                exit(-1)

            query = {'ownerId.equals': record[0]['owner']['id'], 'type': 'LAYER'}
            response = requests.get(f'{endpoint}/app/api/group-layers', params=query, headers=auth_header)
            if response.status_code == 200:
                record = response.json()
                if len(groups) == 1:
                    print('VISAO_LAYER=%s' % record[0]['id'])
                elif len(groups) > 1:
                    print('Warning: more than one project group')
                else:
                    print('No group layer found for this user')
            else:
                print('No layer defined')
                exit(-1)

            print(f'{endpoint}/app/visao/{settings.VISAO_LAYOUT}?' \
                  f'grupCategory={settings.VISAO_GROUP}' \
                  f'&l={settings.VISAO_LAYER}&e=f')

        elif options['topics']:
            self.populate_topics()

        elif options['delete']:
            auth_header = visao.authenticate()
            delete_dataset(auth_header, options['delete'])

        elif options['projects']:
            print('Creating/Updating projects')
            self.populate_projects()

        else:
            print('No function specified')
