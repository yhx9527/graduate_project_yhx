import dash_html_components as html
layout = html.Div([
    html.Pre([
        '尝试分析一下',
        html.I(className='fa fa-line-chart'),
        html.Span(' '),
        html.A('央视新闻', href='javascript:void(0);', id='example-analyse1'),
        html.Span(', '),
        html.A('66598046050', href='javascript:void(0);', id='example-analyse2'),
    ], className='website-info'),
    html.Div([
        html.Div('', className='tile is-2'),
        html.Div([
            html.Div([
                    html.Div([
                        html.A([
                            html.Div([
                                html.Span('统计')
                            ],className='timeline-year'),
                            html.Div([
                                html.I(className='fa fa-rocket')
                            ],className='timeline-icon'),
                            html.Div('数据统计', className='title'),
                            html.P('将用户的视频作品的点赞，时长等进行数据统计，并通过可视化呈现', className='description')
                        ], className='timeline-content', href='#')
                    ],className='timeline'),
                    html.Div([
                        html.A([
                            html.Div([
                                html.Span('词云')
                            ],className='timeline-year'),
                            html.Div([
                                html.I(className='fa fa-rocket')
                            ],className='timeline-icon'),
                            html.Div('生成词云', className='title'),
                            html.P('对用户的视频描述使用jieba的TFIDF分词方法逐一分词，将分词结果通过词云进行呈现', className='description')
                        ], className='timeline-content', href='#')
                    ],className='timeline'),
                    html.Div([
                        html.A([
                            html.Div([
                                html.Span('主题')
                            ],className='timeline-year'),
                            html.Div([
                                html.I(className='fa fa-rocket')
                            ],className='timeline-icon'),
                            html.Div('短文本主题建模', className='title'),
                            html.P('使用Gibbs采样的Dirichlet混合模型将视频描述文本进行主题聚类操作，最终将模型训练结果使用pyLDAvis进行可视化呈现', className='description')
                        ], className='timeline-content', href='#')
                    ],className='timeline'),
                    html.Div([
                        html.A([
                            html.Div([
                                html.Span('联系')
                            ],className='timeline-year'),
                            html.Div([
                                html.I(className='fa fa-rocket')
                            ],className='timeline-icon'),
                            html.Div('用户关联性分析', className='title'),
                            html.P('将用户的分词结果作为标签使用已训练好的doc2vec模型进行分析，最终得出与所分析用户最相似的用户',
                                   className='description')
                        ], className='timeline-content', href='#')
                    ],className='timeline'),
                ],className='main-timeline')
        ], className='tile is-8 timeline-container', )
    ], className='tile is-ancestor')
], id='info_analyse')

