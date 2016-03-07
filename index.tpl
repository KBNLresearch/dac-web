<!DOCTYPE html>
<html>
<head>
    <title>Training named entities</title>
    <meta charset="UTF-8">
    <style>
    * {margin: 0; padding: 0; border: 0;}
    .link {float: right; display: block; height: 80px; line-height: 80px; padding: 0 10px;}
    </style>
</head>
<body style="font-family: verdana, sans-serif; color: #3B3131;">
    <!-- Header -->
    <div id="heading" style="position: fixed; width: 90%; height: 80px; padding: 0 5%; background-color: #ddd;">
        <h1 style="float: left; line-height: 80px;">Training instance {{index}} of {{last_instance}}</h1>
        <a class="link" href="javascript: document.getElementById('action').value = 'last'; document.forms['form'].submit();">last</a>
        <a class="link" href="javascript: document.getElementById('action').value = 'first'; document.forms['form'].submit();">first</a>
        <a class="link" href="javascript: document.getElementById('action').value = 'next'; document.forms['form'].submit();">next</a>
        <a class="link" href="javascript: document.getElementById('action').value = 'prev'; document.forms['form'].submit();">prev</a>
    </div>
    <!-- Named entity, article OCR -->
    <div id="ocr" style="width: 45%; position: fixed; top: 80px; right: 50%; padding-left: 5%;">
        <h2 style="margin-top: 20px; height: 30px;">Newspaper article</h2>
        <p style="font-weight: bold; font-size: 12px; margin-top: 20px; height: 24px; line-height: 12px;">Current entity: {{ne}}</>
        <p style="font-weight: bold; font-size: 12px; margin-bottom: 44px; height: 24px; line-height: 12px;">Article url: {{url}}</p>
        <div id="scroll1" style="overflow-y: scroll; margin-right: 20px; padding-right: 10px;">
            <p>{{!ocr}}</p>
        </div>
    </div>
    <!-- DBpedia candidates -->
    <div id="dbp" style="width: 45%; position: fixed; top: 80px; left:50%; padding-right: 5%;">
        <h2 style="margin-top: 20px; height: 30px;">DBpedia candidates</h2>
        <p style="font-weight: bold; font-size: 12px; margin: 20px 0 0 0; height: 24px; line-height: 12px;">Da: {{da_link}}</p>
        <p style="font-weight: bold; font-size: 12px; margin: 0; height: 24px; line-height: 12px;">Dac: {{dac_link}}</p>
        <p style="font-weight: bold; font-size: 12px; margin-bottom: 20px; height: 24px; line-height: 12px;">Current: {{link}}</p>
        <div id="scroll2" style="overflow-y: scroll; margin-right: 0px; padding-right: 10px;">
        <form id="form" method="post" action="">
        % if hasattr(solr_results, 'numFound'):
        % for res in solr_results:
            <div class="candidate" style="margin-bottom: 20px;">
                % id_parts = res['id'].split('/')
                % display_name = id_parts[-1][:-1]
                <p style="font-weight: bold; margin-bottom: 10px;"><input style="margin-right: 10px;" type="radio" name="link" value="{{res['id'][1:-1]}}" {{!"checked" if link == res['id'][1:-1] else ""}} />{{display_name}}</p>
                <p>Titles:
                    <ul style="margin-left: 20px;">
                    % for t in res['title']:
                        % if len(t) > 1:  
                        <li>{{t}}</li>
                        % end
                    % end
                    </ul>
                </p>
                <p>Abstract: {{res['abstract'] if 'abstract' in res else ''}}</p>
                <p>Language: {{res['lang']}}</p>
                <p>Inlinks: {{res['inlinks']}}</p>    
            </div>
        % end
        % end
        <div class="candidate" style="margin-bottom: 20px;">
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
            <p style="font-weight: bold; margin-bottom: 10px;"><input id="other_radio" style="margin-right: 10px;" type="radio" name="link" value="other" {{!"checked" if other_link else ""}} />Other</p>
            <p>Enter a DBpedia identifier not shown in the list above <br/>(e.g. http://dbpedia.org/resource/Ruskie_Business):</p>
            <input id="other_input" type="text" name="other_link" value="{{!link if other_link else ""}}" style="width: 90%; border: 1px solid #eee; padding: 5px; margin-top: 5px; font-family: verdana, sans-serif;"></input>
        </div>
        <div class="candidate" style="margin-bottom: 20px;">
            <p style="font-weight: bold; margin-bottom: 10px;"><input style="margin-right: 10px;" type="radio" name="link" value="none" {{!"checked" if (link == 'none' or link == '') else ""}} />Not found</p>
            <p>Select this option if no matching candidate can be found.</p>
        </div>
        <input type="hidden" name="index" value="{{index}}" />
        <input type="hidden" name="action" id="action" value="" />
        </form>
        </div>
    </div>
    <script>
        var window_height = window.innerHeight;
        var scroll_height = window_height - 260;
        document.getElementById("scroll1").style.height = scroll_height + "px";
        document.getElementById("scroll2").style.height = scroll_height + "px";
        document.getElementById("other_input").onfocus = function(){
            document.getElementById("other_radio").checked = true;
        };
    </script>
</body>
</html>

