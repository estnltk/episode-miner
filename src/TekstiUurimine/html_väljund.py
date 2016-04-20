'''
Created on 19.04.2016

@author: paul
'''
import json

def frequent_episodes_to_html(episodes):
    html_text = ''
    for i in range(len(episodes)):
        html_text += '<p><a href="' + str(i) + '.html">'
        html_text += str(round(episodes[i][0], 3)) + ': '
        for event_type in episodes[i][1]:
            html_text += '<span class="highlight">' +  event_type + '</span> &rarr; '
        html_text = html_text[:-7] + '</a></p>\n'
    with open('/home/paul/workspace/MyTestProject/data/html_template', 'r') as f:
        html_template = f.read()
    
    html = html_template.format(html_text) 
    
    with open('/home/paul/workspace/MyTestProject/data/html/index.html', 'w') as f:
        f.write(html)


def examples_of_frequent_episodes_to_html(episodes, examples_of_frequent_episodes):
    with open('/home/paul/workspace/MyTestProject/data/html_template', 'r') as f:
        html_template = f.read()
    f.closed
    for i in range(len(episodes)):
        examples = examples_of_frequent_episodes[i]
        html_text = ''
        for example in examples:
            example_text = example[0]
            html_text += '<p>'
            for j in range(len(example[1])-1):
                html_text += '<span class="highlight">' + example_text[example[1][j][0] : example[1][j][1]] + '</span>' + example_text[example[1][j][1] : example[1][j+1][0]]
            html_text += '<span class="highlight">' + example_text[example[1][-1][0]: example[1][-1][1]] + '</span>'
            html_text += '</p>\n'
        html = html_template.format(html_text) 
    
        with open('/home/paul/workspace/MyTestProject/data/html/'+str(i)+'.html', 'w') as f:
            f.write(html)
        f.closed

with open('/home/paul/workspace/MyTestProject/data/frequent_episodes.json', 'r') as f:
    frequent_episodes = json.load(f)
with open('/home/paul/workspace/MyTestProject/data/examples_of_frequent_episodes.json', 'r') as f:
    examples_of_frequent_episodes = json.load(f)

frequent_episodes_to_html(frequent_episodes)
examples_of_frequent_episodes_to_html(frequent_episodes, examples_of_frequent_episodes)
