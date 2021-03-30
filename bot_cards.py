help_card_admin = """
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
                                    "width": "stretch",
                                    "items": [
                                        {{
                                            "type": "TextBlock",
                                            "text": "GoCSAP Bot",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        }},
                                        {{
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "Admin Help",
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
            "text": "Hello! 👋 I'm your GoCSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program.",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "Your current GoCSAP bot access level: **{level}**.",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "{adminInfo}",
            "wrap": true
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "View Commands",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "🙋 **I understand the following commands:**",
                                "spacing": "ExtraLarge"
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`subscribe`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Subscribe to GoCSAP bot updates.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`unsubscribe`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Unsubscribe from GoCSAP bot updates.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`help`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Open GoCSAP bot information.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`contact`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Contact the team behind the GoCSAP bot.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`make admin`"
                                            }},
                                            {{
                                                "type": "TextBlock",
                                                "text": "`make superadmin`",
                                                "spacing": "None"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Submit a request for GoCSAP bot admin access. Followed by a Cisco email address when requesting for someone else.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "Small"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "View Admin Commands",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "🔥 **I understand the following admin commands:**"
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`send notif`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Submit a notification to be sent to all GoCSAP bot subscribers.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`analytics`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Request GoCSAP bot analytics.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`cancel admin`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Revoke all admin rights. Followed by a Cisco email address when revoking for someone else (only superadmins can revoke for someone else).",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

approve_card = """
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {{
    "type": "AdaptiveCard",
    "body": [
        {{
            "type": "TextBlock",
            "text": "Your message with message ID {msg_id} has been sent for review. Please approve or decline the message to be sent to all bot subscribers.",
            "wrap": true
        }},
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {{
                            "type": "ActionSet",
                            "actions": [
                                {{
                                    "type": "Action.Submit",
                                    "title": "Decline",
                                    "style": "destructive",
                                    "id": "decline_msg",
                                    "data": "decline_msg"
                                }},
                                {{
                                    "type": "Action.Submit",
                                    "title": "Approve",
                                    "style": "positive",
                                    "id": "approve_msg",
                                    "data": "approve_msg"
                                }}
                            ],
                            "horizontalAlignment": "Left",
                            "spacing": "None"
                        }}
                    ]
                }}
            ],
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

analytics_card = """
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
                            "type": "TextBlock",
                            "text": "GoCSAP Bot, {today_date}",
                            "weight": "Lighter",
                            "color": "Accent"
                        }},
                        {{
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "Admin Analytics",
                            "horizontalAlignment": "Left",
                            "wrap": true,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "📊 Welcome to the GoCSAP bot admin analytics. You can view a summary of statistics below, or pull a detailed report by clicking the **Pull Report** button.",
                            "wrap": true
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "width": 35,
                    "items": [
                        {{
                            "type": "TextBlock",
                            "text": "Total subscribers:",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "Total admins:",
                            "spacing": "ExtraLarge"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "Total superadmins:",
                            "spacing": "Small"
                        }}
                    ]
                }},
                {{
                    "type": "Column",
                    "width": 50,
                    "items": [
                        {{
                            "type": "TextBlock",
                            "text": "{nr_subscribers}",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "{nr_admins}",
                            "spacing": "ExtraLarge"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "{nr_superadmins}",
                            "spacing": "Small"
                        }}
                    ]
                }}
            ],
            "spacing": "Padding",
            "horizontalAlignment": "Center"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.Submit",
                    "title": "Pull Report",
                    "data":  "pull_report"
                }}
            ],
            "horizontalAlignment": "Left",
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

request_admin_card = """
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
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "New {level} access request",
                            "horizontalAlignment": "Left",
                            "wrap": true,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "**{requestor}** requested **{level}** access to the GoCSAP bot. Please approve or decline the request.",
                            "wrap": true
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "What is this?",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "You are a superadmin for the GoCSAP bot, therefore your approval is required when admin/superadmin requests are submitted.",
                                "wrap": true
                            }},
                            {{
                                "type": "FactSet",
                                "facts": [
                                    {{
                                        "title": "Admin",
                                        "value": "Can submit notifications through the GoCSAP bot which are sent to all bot subscribers and can request GoCSAP bot analytics."
                                    }},
                                    {{
                                        "title": "Superadmin",
                                        "value": "Have admin rights and can approve new admins/superadmins."
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "None"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.Submit",
                    "title": "Decline",
                    "id": "Decline",
                    "data": "decline_admin {requestor} {level}"
                }},
                {{
                    "type": "Action.Submit",
                    "title": "Approve",
                    "id": "Approve",
                    "data": "approve_admin {requestor} {level}"
                }}
            ],
            "spacing": "None",
            "horizontalAlignment": "Left"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

greeting_card = """
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
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "100px",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "altText": "",
                                            "url": "https://i.pinimg.com/originals/54/68/bf/5468bf0cb6dcdeab64c17731dac360ae.gif",
                                            "horizontalAlignment": "Left"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "CSAP Bot",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "Welcome!",
                                            "horizontalAlignment": "Left",
                                            "wrap": true,
                                            "color": "Light",
                                            "size": "Large",
                                            "spacing": "Small"
                                        }
                                    ],
                                    "verticalContentAlignment": "Center"
                                }
                            ]
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Hello, I'm your GoCSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program!",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "📋 **GoCSAP bot content includes:**",
            "spacing": "ExtraLarge"
        },
        {
            "type": "TextBlock",
            "text": "• General CSAP infos and news",
            "spacing": "Padding",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "• Notifications about events",
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "• Get updated on the latest newsletters created by CSAPers",
            "height": "stretch",
            "wrap": true,
            "spacing": "Small"
        }],
    "actions": [{"type": "Action.Submit",
                         "title": "Subscribe",
                         "data": "subscribe",
                         "style": "positive",
                         "id": "button1"
                        },
                        {"type": "Action.OpenUrl",
                         "title": "More Info",
                         "url": "https://cisco.sharepoint.com/sites/CSAPGlobal/SitePages/CSAP%20Live.aspx"
                        },
                        {"type": "Action.Submit",
                         "title": "Unsubscribe",
                         "data": "unsubscribe",
                         "style": "positive",
                         "id": "button3" 
                        }
                        ],
    
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """

help_card = """
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
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "GoCSAP Bot",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "Help",
                                            "horizontalAlignment": "Left",
                                            "wrap": true,
                                            "color": "Light",
                                            "size": "Large",
                                            "spacing": "Small"
                                        }
                                    ],
                                    "verticalContentAlignment": "Center"
                                }
                            ]
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Hello! 👋 I'm your GoCSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program.",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "I was especially designed to keep you up to date on the most important topics around CSAP. ",
            "wrap": true
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.ShowCard",
                    "title": "View Commands",
                    "card": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🙋 **I understand the following commands:**",
                                "spacing": "ExtraLarge"
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`subscribe`"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Subscribe to GoCSAP bot updates.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`unsubscribe`"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Unsubscribe from GoCSAP bot updates.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`help`"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Open GoCSAP bot information.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`contact`"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Contact the team behind CSAP bot.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`make admin`"
                                            },
                                            {
                                                "type": "TextBlock",
                                                "text": "`make superadmin`",
                                                "spacing": "None"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Submit a request for GoCSAP bot admin access. Followed by a Cisco email address when requesting for someone else.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "spacing": "Small"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """