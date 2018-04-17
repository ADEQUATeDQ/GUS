from flask import Flask, request, jsonify
from flask_restplus import Api, Resource
import gitlab
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import datetime
import argparse

import rdflib
from rdflib import Namespace, URIRef, RDF, BNode, Literal

from gus.description import DESCRIPTION

DCAT = Namespace("http://www.w3.org/ns/dcat#")
CSVW = Namespace("http://www.w3.org/ns/csvw#")
PROV = Namespace("http://www.w3.org/ns/prov#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

app = Flask(__name__)
api = Api(app)


upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)
upload_parser.add_argument('filename', location='form')
upload_parser.add_argument('sup', location='files',
                           type=FileStorage, required=False)
upload_parser.add_argument('supname', location='form', required=False)


def external_prov(graph, folder):
    activity = BNode()
    graph.add((activity, RDF.type, PROV.Activity))
    graph.add((activity, PROV.startedAtTime, Literal(datetime.datetime.now())))
    graph.add((activity, PROV.endedAtTime, Literal(datetime.datetime.now())))

    agent = BNode(folder)
    graph.add((agent, RDF.type, PROV.Agent))
    graph.add((agent, FOAF.name, Literal(folder)))
    graph.add((activity, PROV.wasAssociatedWith, agent))
    return activity


@api.route('/update')
@api.response(200, 'Project was forked, updated and the info successfully returned.')
@api.response(404, 'Corresponding Gitlab project not found.')
@api.expect(upload_parser)
@api.doc(params={'original': 'URL of the original file', 'folder': 'folder under which new files and metadata.jsonld should be generated', 'token': 'Gitlab authenticfication token'})
class HelloWorld(Resource):
    def post(self):
        git_url = app.config['GITLAB']
        local_url = app.config['LOCAL']

        original = request.args.get("original")
        token = request.args.get("token")
        folder = request.args.get("folder", 'mod')
        # e.g. www_opendataportal_at/all_course_events_2016w/raw/master/cleaned/All_course-events_WS16

        uploaded_file = request.files['file']  # This is FileStorage instance
        filename = request.form.get('filename')
        if not filename and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)
        data = uploaded_file.read()


        # get project name and group
        url_parts = original.replace(git_url, '').split('/')
        group = url_parts[0]
        project_id = url_parts[1]
        orig_filename = url_parts[-1]

        gl = gitlab.Gitlab(local_url, private_token=token)
        # get the project by group/project_id
        p_id = group + '%2F' + project_id
        project = gl.projects.get(p_id)

        # fork project
        fork = project.forks.create({})
        f_id = fork.id
        f_project = gl.projects.get(f_id)

        # create new file(s)
        f = f_project.files.create({'file_path': folder + '%2F' + filename,
                                  'branch': 'master',
                                  'content': data,
                                  'commit_message': 'Created file ' + folder + '/' + filename})

        # get supplementary file
        sup_file = request.files.get('sup')
        if sup_file:
            supname = request.form.get('supname')
            if not supname and sup_file.filename:
                supname = secure_filename(sup_file.filename)
            sup_data = sup_file.read()
            f = f_project.files.create({'file_path': folder + '%2F' + supname,
                                      'branch': 'master',
                                      'content': sup_data,
                                      'commit_message': 'Created file ' + folder + '/' + supname})

        # get metadata file
        metadata = f_project.files.get(file_path='metadata.jsonld', ref='master')
        g = rdflib.Graph()
        g.parse(data=metadata.decode(), format='json-ld')

        # update metadata
        repo_name = f_project.path_with_namespace
        dataset_ref = g.value(predicate=RDF.type, object=DCAT.Dataset)
        # add new resource
        git_res_page = git_url + repo_name + '/' + 'tree/master/' + folder + '/' + filename
        git_res_raw = git_url + repo_name + '/' + 'raw/master/' + folder + '/' + filename

        distribution = URIRef(git_res_page)
        access_url = URIRef(git_res_raw)

        g.add((dataset_ref, DCAT.distribution, distribution))
        g.add((distribution, RDF.type, DCAT.Distribution))
        g.add((distribution, DCAT.accessURL, access_url))

        # prov information
        g.add((access_url, RDF.type, PROV.Entity))
        g.add((access_url, PROV.wasDerivedFrom, URIRef(original)))
        activity = external_prov(g, folder)
        g.add((access_url, PROV.wasGeneratedBy, activity))
        g.add((activity, PROV.generated, access_url))

        # update metadata file
        metadata.content = g.serialize(format='json-ld')
        metadata.save(branch='master', commit_message='Updated metadata.jsonld')

        return jsonify({'file': git_res_raw, 'project': git_url + repo_name})


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--gitlab', help='URL of Gitlab instance. Default: http://data.adequate.at/', default='http://data.adequate.at/')
    parser.add_argument('--local-gitlab', help='Local Gitlab URL (if service is running on same server). Defaults to --gitlab if not set.')
    parser.add_argument('--port', help='Default: 5000', type=int, default=5000)
    args = parser.parse_args()

    app.config['GITLAB'] = args.gitlab

    if args.local_gitlab:
        app.config['LOCAL'] = args.local_gitlab
    else:
        app.config['LOCAL'] = args.gitlab

    app.run(debug=False, host='0.0.0.0', port=args.port)


if __name__ == '__main__':
    main()
