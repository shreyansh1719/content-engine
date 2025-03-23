"""
Default Ad Patterns Database - Contains embedded database of advertising patterns with engagement metrics

This module provides a default database of advertising patterns when no external database files are available.
"""

# Default patterns database with engagement metrics
DEFAULT_AD_PATTERNS = {
    "industries": {
        "technology": {
            "headline_patterns": [
                {
                    "id": "tech_innovation_focus",
                    "pattern": "innovation_focus",
                    "template": "Introducing the [Product] that Changes Everything",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.7,
                        "click_through_rate": 3.2,
                        "conversion_rate": 2.1,
                        "social_sharing_rate": 1.8,
                        "platform_performance": {
                            "instagram": 5.3,
                            "facebook": 3.9,
                            "linkedin": 4.1
                        },
                        "ab_test_insights": "Adding specific numbers increases CTR by 27%"
                    },
                    "examples": [
                        {
                            "headline": "Introducing the MacBook Air that Changes Everything",
                            "performance_score": 4.5,
                            "platform": "instagram"
                        },
                        {
                            "headline": "Introducing the Galaxy S22: The Phone that Changes Everything",
                            "performance_score": 4.8,
                            "platform": "facebook"
                        }
                    ],
                    "best_for": ["new_products", "major_updates"],
                    "demographic_performance": {
                        "18-24": 5.2,
                        "25-34": 4.9,
                        "35-44": 4.5,
                        "45-54": 3.8,
                        "55+": 3.1
                    }
                },
                {
                    "id": "tech_problem_solution",
                    "pattern": "problem_solution",
                    "template": "Tired of [pain point]? The new [Product] solves it with [key feature]",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.2,
                        "click_through_rate": 4.1,
                        "conversion_rate": 3.3,
                        "social_sharing_rate": 0.9,
                        "platform_performance": {
                            "facebook": 6.1,
                            "youtube": 4.8,
                            "instagram": 3.7
                        },
                        "ab_test_insights": "Specific pain points outperform generic ones by 42%"
                    },
                    "examples": [
                        {
                            "headline": "Tired of your laptop dying midday? The new Dell XPS solves it with 24-hour battery life",
                            "performance_score": 5.8,
                            "platform": "facebook"
                        }
                    ],
                    "best_for": ["problem_aware_audience", "feature_heavy_products"],
                    "demographic_performance": {
                        "18-24": 4.3,
                        "25-34": 5.7,
                        "35-44": 5.9,
                        "45-54": 4.5,
                        "55+": 3.6
                    }
                },
                {
                    "id": "tech_specification_highlight",
                    "pattern": "specification_highlight",
                    "template": "[Number] TB of Storage. [Number] Hours of Battery. Endless Possibilities.",
                    "engagement_metrics": {
                        "average_engagement_rate": 3.8,
                        "click_through_rate": 3.5,
                        "conversion_rate": 2.8,
                        "social_sharing_rate": 1.1,
                        "platform_performance": {
                            "facebook": 3.9,
                            "linkedin": 4.5,
                            "instagram": 3.0
                        },
                        "ab_test_insights": "Three specifications outperform two or four"
                    },
                    "examples": [
                        {
                            "headline": "1TB of Storage. 20 Hours of Battery. 64MP Camera. Endless Possibilities.",
                            "performance_score": 4.1,
                            "platform": "linkedin"
                        }
                    ],
                    "best_for": ["tech_savvy_audience", "comparison_shoppers"],
                    "demographic_performance": {
                        "18-24": 3.2,
                        "25-34": 4.1,
                        "35-44": 4.3,
                        "45-54": 3.9,
                        "55+": 3.0
                    }
                }
            ],
            "visual_approaches": [
                {
                    "id": "tech_minimalist_product",
                    "pattern": "minimalist_product",
                    "description": "Clean backgrounds (white/black), dramatic lighting, product as hero",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.2,
                        "platform_performance": {
                            "instagram": 5.7,
                            "pinterest": 4.9,
                            "facebook": 3.8
                        },
                        "average_time_spent": 4.2,
                        "optimal_product_angle": "30° perspective view (38% higher engagement)",
                        "color_impact": "White backgrounds perform 22% better than black for light products",
                        "text_overlay_performance": "Minimal text (1-5 words) increases sharing by 46%"
                    },
                    "ideal_prompt": "Professional product photography of [product] on clean [color] background with dramatic lighting highlighting the [specific_feature], minimalist composition, white space, premium product photography, 30-degree perspective view",
                    "examples": [
                        {
                            "description": "iPhone on white background with dramatic side lighting",
                            "performance_score": 5.3,
                            "platform": "instagram"
                        }
                    ]
                },
                {
                    "id": "tech_lifestyle_integration",
                    "pattern": "lifestyle_integration",
                    "description": "Product seamlessly incorporated into aspirational lifestyle scenarios",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.1,
                        "platform_performance": {
                            "facebook": 5.9,
                            "instagram": 7.2,
                            "pinterest": 4.1
                        },
                        "average_time_spent": 5.7,
                        "demographic_impact": "18-34 age group (6.2% ER), 35-49 (4.7% ER), 50+ (3.1% ER)",
                        "most_effective_settings": "Coffee shops (+32%), home offices (+28%), outdoor leisure (+37%)",
                        "human_element": "Partial human inclusion outperforms full human or no human by 41%"
                    },
                    "ideal_prompt": "Lifestyle photography of [product] being used in a [setting] environment. Partial human element (hands or cropped view) interacting with the device. Soft natural lighting, shallow depth of field, premium lifestyle photography, aspirational scene",
                    "examples": [
                        {
                            "description": "Person using laptop in modern coffee shop with latte nearby",
                            "performance_score": 6.8,
                            "platform": "instagram"
                        }
                    ]
                }
            ],
            "color_schemes": [
                {
                    "id": "tech_apple_style",
                    "pattern": "apple_style",
                    "description": "White backgrounds, minimal color palette, product as color accent",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.6,
                        "color_distribution": "70% white, 20% product color, 10% accent",
                        "effective_product_colors": "Blue (+27%), Red (+24%), Purple (+22%)",
                        "text_color_performance": "Black text on white (4.9% CTR), White text on product color (3.7% CTR)",
                        "platform_performance": {
                            "instagram": 5.8,
                            "pinterest": 5.2,
                            "facebook": 4.1
                        },
                        "seasonal_variation": "Minimal (less than 5% variation across seasons)"
                    }
                },
                {
                    "id": "tech_microsoft_style",
                    "pattern": "microsoft_style",
                    "description": "Vibrant color blocks (blues, greens, yellows, reds) with clean typography",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.2,
                        "color_distribution": "60% solid color blocks, 30% product, 10% white space",
                        "effective_color_combinations": "Blue/green (+31%), blue/orange (+27%)",
                        "text_color_performance": "White text on color blocks (4.7% CTR)",
                        "platform_performance": {
                            "facebook": 4.6,
                            "linkedin": 5.3,
                            "instagram": 3.9
                        }
                    }
                }
            ],
            "copy_structures": [
                {
                    "id": "tech_feature_benefit",
                    "pattern": "feature_benefit",
                    "description": "Feature-Benefit Structure with Technical Details",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.8,
                        "optimal_length": "3 feature-benefit pairs",
                        "format_performance": "Bullets outperform paragraphs by 31%",
                        "word_count_impact": "50-75 words optimal (CTR drops 23% above 100 words)",
                        "technical_language": "2-3 technical terms optimal (engagement drops with 4+)",
                        "order_impact": "Leading with strongest benefit increases CTR by 34%",
                        "question_usage": "Ads with one question perform 27% better than those with none or multiple"
                    },
                    "template": "[Headline Question?]\n\n[Product] delivers:\n• [Feature 1]: [Benefit 1]\n• [Feature 2]: [Benefit 2]\n• [Feature 3]: [Benefit 3]\n\n[CTA]"
                }
            ],
            "emotional_triggers": [
                {
                    "id": "tech_achievement",
                    "pattern": "achievement",
                    "description": "Emphasizing personal accomplishment and capabilities",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.3,
                        "conversion_impact": "+28% for productivity tools, +17% for personal devices",
                        "demographic_performance": {
                            "professionals": 6.2,
                            "students": 5.7,
                            "creatives": 5.1
                        },
                        "best_performing_phrases": [
                            "Do more than you ever thought possible",
                            "Achieve your full potential",
                            "Your best work starts here"
                        ]
                    }
                },
                {
                    "id": "tech_simplification",
                    "pattern": "simplification",
                    "description": "Reducing complexity and making life easier",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.9,
                        "conversion_impact": "+32% for software, +24% for consumer electronics",
                        "demographic_performance": {
                            "non-technical_users": 5.8,
                            "busy_professionals": 5.5,
                            "seniors": 6.3
                        },
                        "best_performing_phrases": [
                            "Technology that just works",
                            "Simplify your [task/process]",
                            "Effortlessly [benefit]"
                        ]
                    }
                }
            ],
            "calls_to_action": [
                {
                    "id": "tech_discover_cta",
                    "pattern": "discover",
                    "text": "Discover More",
                    "engagement_metrics": {
                        "average_click_rate": 4.2,
                        "conversion_rate": 2.8,
                        "a_b_test_insights": "Outperforms 'Learn More' by 18%",
                        "platform_performance": {
                            "instagram": 4.5,
                            "facebook": 4.1,
                            "linkedin": 3.8
                        }
                    }
                },
                {
                    "id": "tech_shop_now_cta",
                    "pattern": "shop_now",
                    "text": "Shop Now",
                    "engagement_metrics": {
                        "average_click_rate": 4.7,
                        "conversion_rate": 3.5,
                        "a_b_test_insights": "Works best with limited-time offers and clear pricing",
                        "platform_performance": {
                            "facebook": 5.2,
                            "instagram": 4.8,
                            "pinterest": 5.5
                        }
                    }
                }
            ]
        },
        "fashion": {
            "headline_patterns": [
                {
                    "id": "fashion_identity_statement",
                    "pattern": "identity_statement",
                    "template": "Be [adjective]. Be [adjective]. Be Yourself.",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.4,
                        "click_through_rate": 4.3,
                        "conversion_rate": 2.7,
                        "social_sharing_rate": 2.9,
                        "platform_performance": {
                            "instagram": 6.8,
                            "facebook": 4.5,
                            "pinterest": 5.2
                        },
                        "ab_test_insights": "Using contrasting adjectives increases engagement by 31%"
                    },
                    "examples": [
                        {
                            "headline": "Be Bold. Be Elegant. Be Yourself.",
                            "performance_score": 6.2,
                            "platform": "instagram"
                        },
                        {
                            "headline": "Be Fierce. Be Kind. Be Yourself.",
                            "performance_score": 5.9,
                            "platform": "pinterest"
                        }
                    ],
                    "demographic_performance": {
                        "18-24": 6.5,
                        "25-34": 5.8,
                        "35-44": 4.9,
                        "45-54": 3.7,
                        "55+": 2.9
                    }
                },
                {
                    "id": "fashion_seasonal_transition",
                    "pattern": "seasonal_transition",
                    "template": "Your [Season] Wardrobe Starts Here",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.9,
                        "click_through_rate": 3.8,
                        "conversion_rate": 3.1,
                        "social_sharing_rate": 1.5,
                        "platform_performance": {
                            "instagram": 5.3,
                            "facebook": 4.7,
                            "pinterest": 5.8
                        },
                        "ab_test_insights": "Early season campaigns (2-3 weeks before season) outperform mid-season by 47%"
                    },
                    "examples": [
                        {
                            "headline": "Your Summer Wardrobe Starts Here",
                            "performance_score": 5.7,
                            "platform": "instagram"
                        }
                    ],
                    "best_for": ["seasonal_collections", "new_arrivals"],
                    "demographic_performance": {
                        "18-24": 5.2,
                        "25-34": 5.9,
                        "35-44": 4.5,
                        "45-54": 3.8,
                        "55+": 3.2
                    }
                }
            ],
            "visual_approaches": [
                {
                    "id": "fashion_editorial_style",
                    "pattern": "editorial_style",
                    "description": "High-fashion photography with artistic composition and dramatic styling",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.7,
                        "platform_performance": {
                            "instagram": 7.2,
                            "pinterest": 6.3,
                            "facebook": 4.1
                        },
                        "average_time_spent": 5.8,
                        "demographic_impact": "Higher engagement with 18-34 female demographic (+42%)",
                        "color_impact": "Monochromatic color schemes perform 27% better than vibrant multi-color",
                        "setting_performance": "Studio settings outperform outdoor by 18%"
                    },
                    "ideal_prompt": "High fashion editorial photography of [product], dramatic lighting, artistic composition, professional fashion photography, studio setting, monochromatic color scheme, magazine quality, fashion week style"
                },
                {
                    "id": "fashion_street_style",
                    "pattern": "street_style",
                    "description": "Authentic-looking scenarios in urban settings with natural styling",
                    "engagement_metrics": {
                        "average_engagement_rate": 6.2,
                        "platform_performance": {
                            "instagram": 7.8,
                            "tiktok": 8.2,
                            "pinterest": 5.4
                        },
                        "average_time_spent": 6.7,
                        "demographic_impact": "Higher with 18-29 age group (+53% vs other age groups)",
                        "setting_performance": "Urban streets (+41%), coffee shops (+32%), public transit (+27%)",
                        "authenticity_impact": "Candid-looking shots outperform posed by 37%"
                    },
                    "ideal_prompt": "Street style fashion photography of [product] being worn in urban setting, candid moment, natural lighting, authentic street photography, stylish but casual, city backdrop, slightly candid pose"
                }
            ],
            "color_schemes": [
                {
                    "id": "fashion_monochrome",
                    "pattern": "monochrome",
                    "description": "Single color palette with varying shades and tones",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.1,
                        "platform_performance": {
                            "instagram": 6.3,
                            "pinterest": 5.7
                        },
                        "best_performing_colors": "Black (+32%), Navy (+27%), Beige (+24%)",
                        "seasonal_variation": "Fall/Winter performance +41% vs Spring/Summer",
                        "luxury_perception": "Increases luxury perception by 47% vs multi-color"
                    }
                }
            ],
            "emotional_triggers": [
                {
                    "id": "fashion_self_expression",
                    "pattern": "self_expression",
                    "description": "Emphasizing individuality and personal style",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.8,
                        "conversion_impact": "+37% for premium brands, +24% for mid-range",
                        "demographic_performance": {
                            "18-24": 7.2,
                            "25-34": 6.5
                        },
                        "best_performing_phrases": [
                            "Express yourself",
                            "Your style, your rules",
                            "As unique as you are"
                        ]
                    }
                }
            ]
        },
        "food": {
            "headline_patterns": [
                {
                    "id": "food_taste_focused",
                    "pattern": "taste_focused",
                    "template": "Savor the [adjective] Flavor of [Product]",
                    "engagement_metrics": {
                        "average_engagement_rate": 5.9,
                        "click_through_rate": 4.8,
                        "conversion_rate": 3.5,
                        "social_sharing_rate": 2.1,
                        "platform_performance": {
                            "instagram": 7.2,
                            "facebook": 5.7,
                            "pinterest": 6.3
                        },
                        "ab_test_insights": "Specific flavor adjectives outperform generic ones by 43%"
                    },
                    "examples": [
                        {
                            "headline": "Savor the Smoky Flavor of Chipotle Grilled Chicken",
                            "performance_score": 6.5,
                            "platform": "instagram"
                        }
                    ],
                    "best_for": ["restaurants", "packaged_foods", "meal_delivery"],
                    "demographic_performance": {
                        "foodies": 7.3,
                        "health_conscious": 5.8,
                        "convenience_seekers": 4.9
                    }
                }
            ],
            "visual_approaches": [
                {
                    "id": "food_hero_shot",
                    "pattern": "hero_shot",
                    "description": "Close-up of food with perfect styling and lighting",
                    "engagement_metrics": {
                        "average_engagement_rate": 6.7,
                        "platform_performance": {
                            "instagram": 8.3,
                            "pinterest": 7.4,
                            "facebook": 5.9
                        },
                        "average_time_spent": 7.2,
                        "styling_impact": "Styled with props (+29%), minimalist styling (+24%)",
                        "angle_performance": "45-degree angle (+37%), overhead flat-lay (+32%)",
                        "lighting_impact": "Side lighting showing texture outperforms direct lighting by 46%"
                    },
                    "ideal_prompt": "Professional food photography of [product], extreme close-up, perfect styling, side lighting to show texture, shallow depth of field, mouth-watering, 45-degree angle, vibrant colors, magazine quality"
                }
            ]
        },
        "entertainment": {
            "headline_patterns": [
                {
                    "id": "ent_content_volume",
                    "pattern": "content_volume",
                    "template": "[Number] Million Songs at Your Fingertips",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.3,
                        "click_through_rate": 3.7,
                        "conversion_rate": 2.9,
                        "social_sharing_rate": 1.2,
                        "platform_performance": {
                            "instagram": 4.6,
                            "facebook": 4.1,
                            "twitter": 5.2
                        },
                        "ab_test_insights": "Larger numbers increase perceived value by 32%"
                    },
                    "examples": [
                        {
                            "headline": "90 Million Songs at Your Fingertips",
                            "performance_score": 4.9,
                            "platform": "twitter"
                        }
                    ]
                }
            ],
            "visual_approaches": [
                {
                    "id": "ent_device_integration",
                    "pattern": "device_integration",
                    "description": "Content displayed across multiple devices in lifestyle setting",
                    "engagement_metrics": {
                        "average_engagement_rate": 4.8,
                        "platform_performance": {
                            "instagram": 5.2,
                            "facebook": 4.7,
                            "twitter": 3.9
                        },
                        "device_impact": "Multiple devices outperform single device by 29%",
                        "setting_performance": "Home settings (+32%), commuting (+27%), social gatherings (+24%)",
                        "content_visibility": "Clear content on screens increases CTR by 41%"
                    },
                    "ideal_prompt": "Lifestyle photography showing [product/service] content displayed across multiple devices (smartphone, tablet, TV) in a modern home setting, people casually interacting with devices, warm lighting, relaxed atmosphere"
                }
            ]
        }
    },
    "universal_patterns": {
        "headline_structures": [
            {
                "id": "universal_question_format",
                "pattern": "question_format",
                "template": "Looking for [benefit]?",
                "engagement_metrics": {
                    "average_engagement_rate": 5.3,
                    "click_through_rate": 4.7,
                    "a_b_test_insights": "Questions outperform statements by 27% on average",
                    "cross_industry_performance": {
                        "technology": 4.9,
                        "fashion": 5.2,
                        "food": 5.8,
                        "entertainment": 5.1
                    }
                }
            },
            {
                "id": "universal_how_to",
                "pattern": "how_to_promise",
                "template": "How to [desired outcome] with [product]",
                "engagement_metrics": {
                    "average_engagement_rate": 5.1,
                    "click_through_rate": 4.3,
                    "a_b_test_insights": "Specific outcomes outperform generic promises by 42%",
                    "cross_industry_performance": {
                        "technology": 5.4,
                        "fashion": 4.2,
                        "food": 5.5,
                        "home_goods": 6.2
                    }
                }
            },
            {
                "id": "universal_numbers_list",
                "pattern": "numbers_list",
                "template": "[Number] Ways [Product] Will [Benefit]",
                "engagement_metrics": {
                    "average_engagement_rate": 4.9,
                    "click_through_rate": 4.6,
                    "a_b_test_insights": "Numbers 3, 5, and 7 outperform other numbers by 23%",
                    "cross_industry_performance": {
                        "technology": 5.3,
                        "fashion": 3.8,
                        "food": 5.1,
                        "entertainment": 4.6
                    }
                }
            }
        ],
        "visual_elements": [
            {
                "id": "universal_hero_product",
                "pattern": "hero_product",
                "description": "Clear, well-lit main product image as focal point",
                "engagement_metrics": {
                    "average_engagement_rate": 5.2,
                    "click_through_rate": 4.6,
                    "a_b_test_insights": "Single hero product outperforms multiple products by 37%",
                    "cross_industry_performance": {
                        "technology": 5.6,
                        "fashion": 5.3,
                        "food": 6.2,
                        "beauty": 5.8
                    }
                }
            },
            {
                "id": "universal_human_element",
                "pattern": "human_element",
                "description": "People using/enjoying the product",
                "engagement_metrics": {
                    "average_engagement_rate": 5.7,
                    "click_through_rate": 4.2,
                    "a_b_test_insights": "Authentic-looking people outperform models by 32%",
                    "cross_industry_performance": {
                        "technology": 4.8,
                        "fashion": 6.3,
                        "food": 5.2,
                        "entertainment": 5.9
                    }
                }
            }
        ],
        "ad_text_structures": [
            {
                "id": "universal_apsaa",
                "pattern": "attention_problem_solution_action",
                "description": "Grab attention → Identify problem → Present solution → Clear CTA",
                "engagement_metrics": {
                    "average_engagement_rate": 5.4,
                    "conversion_rate": 3.8,
                    "a_b_test_insights": "Most universal pattern across industries",
                    "length_impact": "60-80 words optimal",
                    "cross_industry_performance": {
                        "technology": 5.3,
                        "fashion": 4.9,
                        "food": 5.6,
                        "entertainment": 5.1
                    }
                }
            }
        ],
        "psychological_triggers": [
            {
                "id": "universal_scarcity",
                "pattern": "scarcity",
                "description": "Limited quantity, time, or availability",
                "engagement_metrics": {
                    "average_engagement_rate": 5.8,
                    "conversion_rate": 4.2,
                    "a_b_test_insights": "Time-based scarcity outperforms quantity-based by 27%",
                    "cross_industry_performance": {
                        "fashion": 6.5,
                        "technology": 5.2,
                        "travel": 6.1,
                        "entertainment": 4.9
                    }
                }
            },
            {
                "id": "universal_social_proof",
                "pattern": "social_proof",
                "description": "Testimonials, user counts, ratings, reviews",
                "engagement_metrics": {
                    "average_engagement_rate": 5.2,
                    "conversion_rate": 3.9,
                    "a_b_test_insights": "Specific numbers outperform general claims by 43%",
                    "cross_industry_performance": {
                        "technology": 5.7,
                        "fashion": 4.8,
                        "food": 5.1,
                        "services": 6.3
                    }
                }
            }
        ],
        "calls_to_action": [
            {
                "id": "universal_get_benefit",
                "pattern": "benefit_focused",
                "text": "Get Your [Benefit] Today",
                "engagement_metrics": {
                    "average_click_rate": 5.2,
                    "conversion_rate": 3.7,
                    "a_b_test_insights": "Specific benefits outperform generic ones by 39%",
                    "cross_industry_performance": {
                        "technology": 5.1,
                        "fashion": 4.9,
                        "food": 5.3,
                        "entertainment": 4.8
                    }
                }
            },
            {
                "id": "universal_shop_now",
                "pattern": "shop_now",
                "text": "Shop Now",
                "engagement_metrics": {
                    "average_click_rate": 4.9,
                    "conversion_rate": 3.5,
                    "a_b_test_insights": "Simple 'Shop Now' outperforms longer CTAs by 21% for direct sales",
                    "cross_industry_performance": {
                        "fashion": 5.7,
                        "technology": 4.5,
                        "beauty": 5.2,
                        "home_goods": 4.8
                    }
                }
            }
        ]
    }
}