<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Training named entities</title>
    <link rel="stylesheet" type="text/css" href="static/global.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
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
            <p><b>Entity</b>: {{ne}}</p>
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
            <p><b>Prediction</b>: <span id="prediction">Loading...</span></p>
            <p><b>Reason</b>: <span id="reason">Loading...</span></p>
            <p><b>Probability</b>: <span id="prob">Loading...</span></p>
        </div>

        <div>
            <form id="form" method="post" action="">
            % if candidates:
            % i = 0
            % for res in [c.document for c in candidates]:
                <div class="candidate" id="{{res['id']}}">
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
                        <p>"id": {{res['id']}}<br/>
                        % if 'last_part' in res:
                        "last_part": {{res['last_part']}}<br/>
                        % end
                        % if 'alt_label' in res:
                        "alt_label": {{', '.join(res['alt_label'])}}<br/>
                        % end
                        % if 'spec' in res:
                        "spec": {{res['spec']}}<br/>
                        % end
                        % if 'schema_type' in res:
                        "schema_type": {{', '.join(res['schema_type'])}}<br/>
                        % end
                        % if 'dbo_type' in res:
                        "dbo_type": {{', '.join(res['dbo_type'])}}<br/>
                        % end
                        % if 'keyword' in res:
                        "keyword": {{', '.join(res['keyword'])}}<br/>
                        % end
                        % if 'birth_year' in res:
                        "birth_year": {{res['birth_year']}}<br/>
                        % end
                        % if 'death_year' in res:
                        "death_year": {{res['death_year']}}<br/>
                        % end
                        "inlinks": {{res['inlinks']}}<br/>
                        "score": {{res['score']}}</p>
                    </div>

                    <p class="panel_header">
                        <a href="javascript:toggle('feat_panel_{{i}}');">Features</a>
                    </p>
                    <div id="feat_panel_{{i}}" style="display: none;" class="panel feat_panel">
                        <p>Loading...</p>
                    </div>
               </div>
            % i += 1
            % end
            % end

            <!-- Other options -->
            <div class="candidate">
                % other_link = True
                % if candidates:
                %   for res in [c.document for c in candidates]:
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

    <script src="static/global.js"></script>
    <script>predict("{{url}}", "{{ne}}");</script>

</body>
</html>
