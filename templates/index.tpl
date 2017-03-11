<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Training named entities</title>
    <link rel="stylesheet" type="text/css" href="/static/global.css">
</head>
<body>

    <!-- Header -->
    <div id="heading">
        <h1>Training instance {{index}} of {{last_instance}}</h1>
        <a class="link" href="javascript: document.getElementById('action').value='last';
            document.forms['form'].submit();">last</a>
        <a class="link" href="javascript: document.getElementById('action').value='first';
            document.forms['form'].submit();">first</a>
        <a class="link" href="javascript: document.getElementById('action').value='next';
            document.forms['form'].submit();">next</a>
        <a class="link" href="javascript: document.getElementById('action').value='prev';
            document.forms['form'].submit();">prev</a>
    </div>

    <!-- Named entity, article OCR -->
    <div id="ocr">
        <h2>Newspaper article</h2>
        <div class="info">
            % dac_url = 'http://www.kbresearch.nl/dac/?debug=1&url=' + url
            <p><b>Url</b>: <a href={{dac_url}} target="_blank">{{url}}</a></p>
            <p><b>Date</b>: {{publ_date}}</p>
            <p><b>Type</b>: {{ne_type}}</p>
            <p><b>Entity</b>: {{ne + ' (' + norm +')'}}</p>
        </div>
        <div>
            <p>{{!ocr}}</p>
        </div>
    </div>

    <!-- DBpedia candidates -->
    <div id="dbp">

        <h2>DBpedia candidates</h2>
        <div class="info">
            <p><b>Selection</b>: {{link}}</p>
            <p><b>Prediction</b>: </p>
            <p><b>Reason</b>: </p>
            <p><b>Probability</b>: </p>
        </div>

        <div>
            <form id="form" method="post" action="">
            % if solr_response and hasattr(solr_response, 'numFound'):
            % i = 0
            % for res in solr_response:
                <div class="candidate">
                    <p class="label">
                        <input type="radio" name="link" value="{{res['id']}}"
                            {{!"checked" if link == res['id'] else ''}} />
                        <b>{{res['label']}}</b> ({{res['lang']}})
                    </p>
                    <p class="abstract">{{res['abstract']}}</p>

                    <p class="panel_header">
                        <a href="javascript:toggle('descr_panel_{{i}}');">Description</a>
                    </p>
                    <div id="descr_panel_{{i}}" style="display: none;" class="panel">
                        <p><b>Identifier</b>: {{res['id']}}</p>
                        % if 'last_part' in res:
                        <p><b>Last part</b>: {{res['last_part']}}</p>
                        % end
                        % if 'alt_label' in res:
                        <p><b>Alt labels</b>: {{', '.join(res['alt_label'])}}</p>
                        % end
                        % if 'schema_type' in res:
                        <p><b>Schema.org types</b>: {{', '.join(res['schema_type'])}}</p>
                        % end
                        % if 'dbo_type' in res:
                        <p><b>DBpedia ontology types</b>: {{', '.join(res['dbo_type'])}}</p>
                        % end
                        % if 'keyword' in res:
                        <p><b>Keywords</b>: {{', '.join(res['keyword'])}}</p>
                        % end
                        % if 'birth_year' in res:
                        <p><b>Birth year</b>: {{res['birth_year']}}</p>
                        % end
                        % if 'death_year' in res:
                        <p><b>Death year</b>: {{res['death_year']}}</p>
                        % end
                        <p><b>Inlinks</b>: {{res['inlinks']}}</p>
                        <p><b>Score</b>: {{res['score']}}</p>
                    </div>

                    <p class="panel_header">
                        <a href="javascript:toggle('feat_panel_{{i}}');">Features</a>
                    </p>
                    <div id="feat_panel_{{i}}" style="display: none;" class="panel">

                    </div>

               </div>
            % i += 1
            % end
            % end

            <!-- Other options -->
            <div class="candidate">
                % other_link = True
                % if solr_response and hasattr(solr_response, 'numFound'):
                %   for res in solr_response:
                %     if link == res['id']:
                %       other_link = False
                %     end
                %   end
                % end
                % if link == 'none' or link == '':
                %   other_link = False
                % end
                <p class="label">
                    <input id="other_radio" type="radio" name="link" value="other"
                        {{!"checked" if other_link else ""}} />
                    <b>Other</b>
                </p>
                <p>Enter a DBpedia identifier not shown in the list above <br/>
                    (e.g. http://dbpedia.org/resource/Ruskie_Business):</p>
                <input id="other_input" type="text" name="other_link"
                    value="{{!link if other_link else ''}}"></input>
            </div>

            <div class="candidate">
                <p class="label">
                    <input type="radio" name="link" value="none"
                        {{!"checked" if (link == 'none' or link == '') else ""}} />
                    <b>Not found</b>
                </p>
                <p>Select this option if no matching candidate can be found.</p>
            </div>

            <input type="hidden" name="index" value="{{index}}" />
            <input type="hidden" name="action" id="action" value="" />
            </form>
        </div>

    </div>

    <script src="/static/global.js"></script>

</body>
</html>
