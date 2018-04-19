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
        <h1>Training instance #{{instance_id}} <small>({{index}} of {{last_instance}})</small></h1>
        <a class="link" href="javascript: document.getElementById('action').value='next_art';
            document.forms['form'].submit();">next article</a>
        <a class="link" href="javascript: document.getElementById('action').value='prev_art';
            document.forms['form'].submit();">prev article</a>
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
            <p><b>Type</b>: {{ne_type if ne_type else 'unknown'}}</p>
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
            <p><b>Selection</b>: {{', '.join(links)}}</p>
            <p><b>Prediction</b>: <span id="prediction">Loading...</span></p>
            <p><b>Reason</b>: <span id="reason">Loading...</span></p>
            <p><b>Probability</b>: <span id="prob">Loading...</span></p>
        </div>

        <div>
            <form id="form" method="post" action="">
            <!-- Nothing found option -->
            <div class="candidate">
                <p class="label">
                    <input type="checkbox" name="links" value="none"
                        {{!"checked" if 'none' in links else ""}} />
                    <b>Not found</b>
                </p>
                <p>Select this option if no matching candidate can be found.</p>
            </div>

            <!-- Regular Solr candidate options -->
            % if candidates:
            % i = 0
            % for res in [c.document for c in candidates]:
                <div class="candidate" id="{{res['id']}}">
                    <p class="label">
                        <input type="checkbox" name="links" value="{{res['id']}}"
                            {{!"checked" if res['id'] in links else ""}} />
                        <b>{{res['label']}}</b> ({{res['lang']}})
                    </p>
                    <p class="abstract">{{res['abstract']}}</p>

                    <p class="panel_header">
                        <a href="javascript:toggle('descr_panel_{{i}}');">Description</a>
                    </p>
                    <div id="descr_panel_{{i}}" style="display: none;" class="panel">
                        <p>
                        % for key in sorted(res):
                        % if '_str' not in key and 'vector' not in key:
                        % if type(res[key]) is list:
                        "{{key}}": {{', '.join(res[key])}}<br/>
                        % else:
                        "{{key}}": {{res[key]}}<br/>
                        % end
                        % end
                        % end
                        </p>
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
                % other_link = None
                % for l in links:
                %   if l != 'none':
                %     if not candidates or l not in [c.document['id'] for c in candidates]:
                %       other_link = l
                %       break
                %     end
                %   end
                % end
                <p class="label">
                    <input id="other_checkbox" type="checkbox" name="links" value="other"
                        {{!"checked" if other_link else ""}} />
                    <b>Other</b>
                </p>
                <p>Enter a DBpedia identifier not shown in the list above:</p>
                <input id="other_input" type="text" name="other_link"
                    value="{{!other_link if other_link else ''}}"></input>
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
