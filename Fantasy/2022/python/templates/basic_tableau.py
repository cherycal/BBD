__author__ = 'chance'
import tableauserverclient as TSC

SERVER = 'https://10ax.online.tableau.com'

tableau_auth = TSC.TableauAuth('chance_st@yahoo.com', 'Becton69!', 'frantasydev764402')
server = TSC.Server(SERVER)
server.version = '3.4'

with server.auth.sign_in(tableau_auth):
    all_datasources, pagination_item = server.datasources.get()
    print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
    print([datasource.name for datasource in all_datasources])

    print(f'Server version {server.version}')

    all_project_items, pagination_item = server.projects.get()
    print([proj.name for proj in all_project_items])

    # create project item
    #new_project = TSC.ProjectItem(name='Example Project', content_permissions='LockedToProject',
    #                              description='Project created for testing')

    # create the project
    #new_project = server.projects.create(new_project)

    all_project_items, pagination_item = server.projects.get()
    print([proj.name for proj in all_project_items])



    server.auth.sign_out()