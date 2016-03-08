<!DOCTYPE html>
<html>
<head>
    <title>Training named entities</title>
    <meta charset="UTF-8">
    <style>
        * {margin: 0; padding: 0; border: 0;}
        body {font-family: verdana, sans-serif; color: #3B3131;}
        h1 {float: left; line-height: 80px;}
        h2 {margin-bottom: 20px;}
        input[type=radio] {margin-right: 10px;}
        input#other_input {width: 90%; border: 1px solid #eee; padding: 5px; margin-top: 5px; font-family: verdana, sans-serif;}
        p.label {font-weight: bold; margin-bottom: 5px;}
        ul {list-style-type: none;}
        div#heading {position: absolute; width: 90%; height: 80px; padding: 0 5%; background-color: #ddd;}
        div#ocr {width: 44%; position: absolute; top: 80px; right: 50%; padding: 2% 1% 2% 5%;}
        div#dbp {width: 44%; position: absolute; top: 80px; left: 50%; padding: 2% 5% 2% 1%;}
        div.info {margin-bottom: 20px; line-height: 30px;}
        div.candidate {margin-bottom: 15px;}
        a.link {float: right; display: block; height: 80px; line-height: 80px; padding: 0 10px;}
    </style>
</head>
<body>
    <!-- Header -->
    <div id="heading">
        <h1>Training instance {{index}} of {{last_instance}}</h1>
        <a class="link" href="javascript: document.getElementById('action').value='last'; document.forms['form'].submit();">last</a>
        <a class="link" href="javascript: document.getElementById('action').value='first'; document.forms['form'].submit();">first</a>
        <a class="link" href="javascript: document.getElementById('action').value='next'; document.forms['form'].submit();">next</a>
        <a class="link" href="javascript: document.getElementById('action').value='prev'; document.forms['form'].submit();">prev</a>
    </div>
    <!-- Named entity, article OCR -->
    <div id="ocr">
        <h2>Newspaper article</h2>
        <div class="info">
            <p>Current entity: {{ne}} ({{ne_type}})</p>
            <p>Article url: {{url}}</p>
            <p>Publication date: {{publ_date}}</p>
        </div>
        <div>
            <p>{{!ocr}}</p>
        </div>
    </div>
    <!-- DBpedia candidates -->
    <div id="dbp">
        <h2>DBpedia candidates</h2>
        <div class="info">
            <p>Da: {{da_link}}</p>
            <p>Dac: {{dac_link}}</p>
            <p>Current: {{link}}</p>
        </div>
        <div>
        <form id="form" method="post" action="">
        % if hasattr(solr_results, 'numFound'):
        % for res in solr_results:
            <div class="candidate">
                % id_parts = res['id'].split('/')
                % display_name = id_parts[-1][:-1]
                <p class="label">
                    <input type="radio" name="link" value="{{res['id'][1:-1]}}" {{!"checked" if link == res['id'][1:-1] else ""}} />
                    {{display_name}}{{' (' + str(res['yob']) + ')' if 'yob' in res else ''}}
                </p>
                % if 'title' in res:
                <p>Titles:
                    <ul>
                    % for t in res['title']:
                        % if len(t) > 1:  
                        <li>{{t}}</li>
                        % end
                    % end
                    </ul>
                </p>
                % end
                % if 'schemaorgtype' in res:
                <p>Types:
                    <ul>
                    % for t in res['schemaorgtype']:
                        % if len(t) > 1:  
                        <li>{{t}}</li>
                        % end
                    % end
                    </ul>
                </p>
                % end
                <p>Abstract: {{res['abstract'] if 'abstract' in res else ''}}</p>
                <p>Language: {{res['lang']}}</p>
                <p>Inlinks: {{res['inlinks']}}</p>    
            </div>
        % end
        % end
        <div class="candidate">
            % other_link = True
            % if hasattr(solr_results, 'numFound'):
            % for res in solr_results:
            % if link == res['id'][1:-1]:
            % other_link = False
            % end
            % end
            % end
            % if link == 'none' or link == '':
            % other_link = False
            % end
            <p class="label"><input id="other_radio" type="radio" name="link" value="other" {{!"checked" if other_link else ""}} />Other</p>
            <p>Enter a DBpedia identifier not shown in the list above <br/>(e.g. http://dbpedia.org/resource/Ruskie_Business):</p>
            <input id="other_input" type="text" name="other_link" value="{{!link if other_link else ""}}"></input>
        </div>
        <div class="candidate">
            <p class="label"><input type="radio" name="link" value="none" {{!"checked" if (link == 'none' or link == '') else ""}} />Not found</p>
            <p>Select this option if no matching candidate can be found.</p>
        </div>
        <input type="hidden" name="index" value="{{index}}" />
        <input type="hidden" name="action" id="action" value="" />
        </form>
        </div>
    </div>
    <script>
        document.getElementById("other_input").onfocus = function(){
            document.getElementById("other_radio").checked = true;
        };
    </script>
</body>
</html>
