# (default) card with 3 image, 2 titles, 3 textboxes, 2 buttons
notif_card_1 = """
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {{
    "type": "AdaptiveCard",
    "body": [
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "items": [
                        {{
                            "type": "ColumnSet",
                            "columns": [
                                {{
                                    "type": "Column",
                                    "width": "100px",
                                    "items": [
                                        {{
                                            "type": "Image",
                                            "altText": "",
                                            "url": "{image_url}",
                                            "horizontalAlignment": "Left"
                                        }}
                                    ]
                                }},
                                {{
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {{
                                            "type": "TextBlock",
                                            "text": "{small_title}",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        }},
                                        {{
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "{main_title}",
                                            "horizontalAlignment": "Left",
                                            "wrap": true,
                                            "color": "Light",
                                            "size": "Large",
                                            "spacing": "Small"
                                        }}
                                    ],
                                    "verticalContentAlignment": "Center"
                                }}
                            ]
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_1}",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_2}",
            "spacing": "ExtraLarge",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_3}",
            "spacing": "Padding",
            "wrap": true
        }},
        {{
        "type": "ActionSet",
    "actions": [{{"type": "Action.OpenUrl",
                         "title": "{button1_text}",
                         "url": "{button1_url}",
                         "horizontalAlignment": "Left"
                        }},
                 {{"type": "Action.OpenUrl",
                         "title": "{button2_text}",
                         "url": "{button2_url}",
                         "horizontalAlignment": "Left"
                        }}
                        ],
                "horizontalAlignment": "Left",
                "spacing": "None"
    }},
    {{
            "type": "TextBlock",
            "text": "Under review: {msg_id}",
            "spacing": "Small",
            "horizontalAlignment": "Right",
            "fontType": "Monospace",
            "size": "Small",
            "weight": "Lighter",
            "color": "Light",
            "isVisible": {isVisible}
    }}
    
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """ #.format(test="ALOHA")

# card with 1 title, 1 textbox
notif_card_2 = """
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {{
    "type": "AdaptiveCard",
    "body": [
        {{
            "type": "Container",
            "items": [
                {{
                    "type": "ColumnSet",
                    "columns": [
                        {{
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {{
                                    "type": "TextBlock",
                                    "weight": "Bolder",
                                    "text": "{main_title}",
                                    "horizontalAlignment": "Left",
                                    "wrap": true,
                                    "color": "Light",
                                    "size": "Large",
                                    "spacing": "Small"
                                }},
                                {{
                                    "type": "TextBlock",
                                    "text": "{textbox_1}",
                                    "wrap": true
                                }}
                            ]
                        }}
                    ],
                    "spacing": "None",
                    "bleed": true
                }}
            ]
        }},
        {{
            "type": "Column",
            "width": "auto",
            "items": [
                {{
                "type": "TextBlock",
                "text": "Under review: {msg_id}",
                "spacing": "Small",
                "horizontalAlignment": "Right",
                "fontType": "Monospace",
                "size": "Small",
                "weight": "Lighter",
                "color": "Light",
                "isVisible": {isVisible}
                }}
            ]
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

# to be filled out - (default) card with 3 image, 2 titles, 3 textboxes, 2 buttons
send_notif_template_1 = """
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Image",
                            "url": "https://i.pinimg.com/originals/54/68/bf/5468bf0cb6dcdeab64c17731dac360ae.gif",
                            "size": "Medium",
                            "height": "50px"
                        }
                    ],
                    "width": "auto"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Small Text",
                            "spacing": "None",
                            "id": "small_title"
                        },
                        {
                            "type": "Input.Text",
                            "placeholder": "Main title",
                            "id": "main_title",
                            "spacing": "None"
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "Container",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 1",
                                    "isMultiline": true,
                                    "id": "textbox_1_card_1"
                                },
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 2",
                                    "isMultiline": true,
                                    "id": "textbox_2",
                                    "spacing": "Small"
                                },
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text Box 3",
                                    "id": "textbox_3",
                                    "isMultiline": true,
                                    "spacing": "Small"
                                },
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "Input.Text",
                                                    "placeholder": "Button 1 text",
                                                    "id": "button1_text"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "Input.Text",
                                                    "placeholder": "Button 2 text",
                                                    "id": "button2_text"
                                                }
                                            ]
                                        }
                                    ],
                                    "spacing": "Small"
                                }
                            ]
                        }
                    ],
                    "spacing": "None",
                    "bleed": true
                }
            ],
            "bleed": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "Input.Text",
                                            "placeholder": "Button URL",
                                            "id": "button1_url"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "Input.Text",
                                            "placeholder": "Button URL",
                                            "id": "button2_url"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "Input.Text",
                            "placeholder": "Image URL",
                            "id": "image_url",
                            "spacing": "None"
                        }
                    ]
                }
            ],
            "horizontalAlignment": "Center",
            "spacing": "ExtraLarge",
            "separator": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Review before sending",
                            "value": "true",
                            "wrap": false,
                            "id": "review",
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "Submit Notification",
                                    "id": "submit_notif_1"
                                    
                                }
                            ],
                            "horizontalAlignment": "Center",
                            "spacing": "None"
                        }
                    ]
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "If **review before sending** is checked, the notification will first be sent to you for review before it is sent to all subscribers.",
            "wrap": true,
            "color": "Light"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """

# to be filled out - card with 1 title, 1 textbox
send_notif_template_2 = """
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Main title",
                                    "id": "main_title",
                                    "spacing": "None"
                                },
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 1",
                                    "isMultiline": true,
                                    "id": "textbox_1_card_2"
                                }
                            ]
                        }
                    ],
                    "spacing": "None",
                    "bleed": true
                }
            ],
            "bleed": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Review before sending",
                            "value": "true",
                            "wrap": false,
                            "id": "review",
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "Submit Notification",
                                    "id": "submit_notif_2"
                                }
                            ],
                            "horizontalAlignment": "Center",
                            "spacing": "None"
                        }
                    ]
                }
            ],
            "separator": true
        },
        {
            "type": "TextBlock",
            "text": "If **review before sending** is checked, the notification will first be sent to you for review before it is sent to all subscribers.",
            "wrap": true,
            "color": "Light"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """

# to be filled out with a personalized card - card with 1 textbox
# can be created on: https://developer.webex.com/buttons-and-cards-designer
send_notif_template_own = """
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 1",
                                    "isMultiline": true,
                                    "id": "textbox_1_card_own"
                                }
                            ]
                        }
                    ],
                    "spacing": "None",
                    "bleed": true
                }
            ],
            "bleed": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Review before sending",
                            "value": "true",
                            "wrap": false,
                            "id": "review",
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "Submit Notification",
                                    "id": "submit_notif_perso"
                                }
                            ],
                            "horizontalAlignment": "Center",
                            "spacing": "None"
                        }
                    ]
                }
            ],
            "separator": true
        },
        {
            "type": "TextBlock",
            "text": "If **review before sending** is checked, the notification will first be sent to you for review before it is sent to all subscribers.",
            "wrap": true,
            "color": "Light"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """