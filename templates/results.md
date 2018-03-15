
# Topics
{% for topic, topicdata in meeting.topics.items() %}
## {{topic}}
  {% for info in topicdata.info %}
        * {{info-}}
  {% endfor %}
{% endfor -%}

# Actions
{% for user, userdata in meeting.users.items() %}
## {{user}}
  {% for action in userdata.actions %}
        * {{action}}
  {% endfor %}
{% endfor %}

# Lines said
{% for user, userdata in meeting.users.items() %}
* {{user}} - {{userdata.message_count-}}
{%endfor%}

# Whole meeting
```
{% for line in meeting.discussion %}
    {{line-}}
{%endfor%}
```
