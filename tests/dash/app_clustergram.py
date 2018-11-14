import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bio
from dash_bio.utils import geneExpressionReader
import base64

colorPalette = [
    'rgb(255,0,0)',
    'rgb(75,150,255)',
    'rgb(150,150,250)'
]

fig_options = dict(
    data=None, cluster='all',
    optimalLeafOrder=False,
    displayRatio=[0.3, 0.1],
    columnLabels=None, rowLabels=None,
    hideLabels=['row'],
    colorThreshold=dict(row=9, col=35),
    height=650, width=650,
    colorMap=[
        [0.0, colorPalette[0]],
        [0.5, colorPalette[1]],
        [1.0, colorPalette[2]]
    ],
    colorList={
        'row': [colorPalette[0], colorPalette[1], colorPalette[2]],
        'col': [colorPalette[1], colorPalette[2], colorPalette[0]],
        'bg': 'rgb(255,255,255)'
    },
    annotationFont=dict(
        color='white',
        size=10
    ),
    tickFont=dict(
        size=10,
        color='rgb(200,200,200)'
    ),
    symmetricValue=True,
    logTransform=True,
    imputeFunction={
        'strategy': 'median',
        'missingValues': 'NaN',
        'axis': 1
    }
)
computedTraces = None

# initialize app with some data
initialFile = './tests/sample_data/E-GEOD-38612-query-results.tpms.tsv'
_, _, initialRows, initialCols = geneExpressionReader.parse_tsv(
    filepath=initialFile,
    rowLabelsSource='Gene Name'
)
# limit the number of initial selected rows for faster loading
initialRows = initialRows[:10]


def description():
    return 'Display hierarchical clustering and a heatmap with this clustergram. \
    Perfect for visualization of gene expression data.'


def layout():
    return html.Div(id='clustergram-body', children=[
        html.Div(
            id='clustergram-header',
            children=[
                'Dash Clustergram'
            ]
        ),

        html.Div(
            id='clustergram-wrapper',
            children=[
            ]
        ),

        html.Div(
            id='clustergram-options', children=[
                html.Div(
                    id='clustergram-file-upload-container',
                    children=[
                        dcc.Upload(
                            id='file-upload',
                            children=html.Div([
                                "Drag and drop .tsv files or select files."
                            ]),
                            filename=initialFile
                        )
                    ],
                    style={
                        'border': 'dotted 2px white',
                        'height': '50px',
                        'width': '230px',
                        'border-radius': '5px',
                        'padding': '10px'
                    }
                ),
                html.Hr(),

                "Rows to display",
                html.Br(),
                dcc.Dropdown(
                    id='selected-rows',
                    multi=True,
                    value=initialRows
                ),
                "Columns to display",
                html.Br(),
                dcc.Dropdown(
                    id='selected-columns',
                    multi=True,
                    value=initialCols
                ),
                html.Hr(),

                "Cluster by:",
                html.Br(),

                dcc.Dropdown(
                    id='cluster-checklist',
                    options=[
                        {'label': 'Row', 'value': 'row'},
                        {'label': 'Column', 'value': 'col'}
                    ],
                    value=['row', 'col'],
                    multi=True
                ),

                html.Hr(),

                "Change color threshold",
                html.Br(),
                html.Div(
                    id='threshold-wrapper',
                    children=[
                        dcc.Slider(
                            id='column-threshold',
                            min=0,
                            max=60,
                            step=0.5,
                            value=35
                        ),
                        html.Br(),
                        dcc.Slider(
                            id='row-threshold',
                            min=0,
                            max=40,
                            step=0.5,
                            value=9
                        )
                    ]
                ),

                html.Hr(),

                "Add or remove all group markers:",
                html.Br(),

                html.Div(
                    id='add-group-markers',
                    children=[
                        dcc.Dropdown(
                            id='row-or-col-group',
                            options=[
                                {'label': 'Row group', 'value': 'row'},
                                {'label': 'Column group', 'value': 'col'}
                            ]
                        ),
                        dcc.Input(
                            id='group-number',
                            placeholder='group number',
                            type='number',
                            value=''
                        ),
                        dcc.Input(
                            id='annotation',
                            placeholder='annotation',
                            type='text',
                            value=''
                        ),
                        dcc.Input(
                            id='color',
                            placeholder='color',
                            type='text',
                            value=''
                        ),
                        html.Button(
                            id='submit-group-marker',
                            children='submit',
                            n_clicks=0,
                            n_clicks_timestamp=0
                        )
                    ]
                ),

                html.Button(
                    id='remove-all-group-markers',
                    children=[
                        "Remove"
                    ],
                    n_clicks=0,
                    n_clicks_timestamp=0
                )

            ]
        ),

        html.Div(
            id='clustergram-info',
            children=[""]
        ),

        html.Div(
            id='trace-storage',
            children=[],
            style={
                'display': 'None'
            }
        )
    ])


def callbacks(app):
    @app.callback(
        Output('selected-rows', 'options'),
        [Input('file-upload', 'contents'),
         Input('file-upload', 'filename')]
    )
    def change_rows_options(contents, filename):
        rowOptions = []
        if contents is None and filename is not None:
            _, _, rowOptions, _ = \
                geneExpressionReader.parse_tsv(
                    filepath=filename,
                    rowLabelsSource='Gene Name'
                )
        else:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('UTF-8')
            _, _, rowOptions, _ = \
                geneExpressionReader.parse_tsv(
                    contents=decoded,
                    rowLabelsSource='Gene Name'
                )
        return [{'label': r, 'value': r} for r in rowOptions]

    @app.callback(
        Output('selected-columns', 'options'),
        [Input('file-upload', 'contents'),
         Input('file-upload', 'filename')]
    )
    def change_cols_options(contents, filename):
        colOptions = []
        if contents is None and filename is not None:
            _, _, _, colOptions = \
                geneExpressionReader.parse_tsv(
                    filepath=filename,
                    rowLabelsSource='Gene Name'
                )
        else:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('UTF-8')
            _, _, _, colOptions = \
                geneExpressionReader.parse_tsv(
                    contents=decoded
                )

        return [{'label': c, 'value': c} for c in colOptions]

    @app.callback(
        Output('clustergram-info', 'children'),
        [Input('file-upload', 'contents'),
         Input('file-upload', 'filename')]
    )
    def display_info(contents, filename):
        if (contents is None and filename is not None):
            _, desc, _, _ = \
                geneExpressionReader.parse_tsv(
                    filepath=filename,
                    rowLabelsSource='Gene Name'
                )
        else:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('UTF-8')
            _, desc, _, _ = \
                geneExpressionReader.parse_tsv(
                    contents=decoded,
                    rowLabelsSource='Gene Name'
                )
        
        infoContent = []
        infoContent.append(html.H3('Information'))
        for key in desc:
            infoContent.append(html.P("{}: {}".format(
                key, desc[key]
            )))

        return infoContent

    @app.callback(
        Output('clustergram-wrapper', 'children'),
        inputs=[Input('submit-group-marker', 'n_clicks'),
                Input('remove-all-group-markers', 'n_clicks'),
                Input('trace-storage', 'children')],
        state=[State('row-or-col-group', 'value'),
               State('group-number', 'value'),
               State('annotation', 'value'),
               State('color', 'value'),
               State('submit-group-marker', 'n_clicks_timestamp'),
               State('remove-all-group-markers', 'n_clicks_timestamp')]
    )
    def add_marker(
            submit_nclicks, removeAll_nclicks, dendro_traces,
            rowOrCol, groupNum, annotation, color,
            submit_time, remove_time
    ):
        if(len(dendro_traces) < 1):
            return html.Div(
                'No data have been selected to display. Please upload a file, \
                then select at least two columns and two rows.',
                style={
                    'padding': '30px',
                    'font-size': '20pt'
                }
            )
        
        global computedTraces
        
        # remove all group markers, if necessary
        if(remove_time > submit_time):
            fig_options['rowGroupMarker'] = []
            fig_options['colGroupMarker'] = []
        else:
            # otherwise, add the appropriate marker
            marker = dict()
            try:
                marker['group'] = int(groupNum)
                marker['annotation'] = annotation
                marker['color'] = color
            except ValueError:
                pass
            if(rowOrCol == 'row'):
                try:
                    fig_options['rowGroupMarker'].append(marker)
                except KeyError:
                    fig_options['rowGroupMarker'] = [marker]
            elif(rowOrCol == 'col'):
                try:
                    fig_options['colGroupMarker'].append(marker)
                except KeyError:
                    fig_options['colGroupMarker'] = [marker]

        try:
            (fig, _) = dash_bio.ClustergramComponent(
                computed_traces=computedTraces, **fig_options
            )
        except ValueError as ve:
            return []
        return dcc.Graph(
            id='clustergram',
            figure=fig
        )

    @app.callback(
        Output('trace-storage', 'children'),
        [Input('file-upload', 'filename'),
         Input('cluster-checklist', 'value'),
         Input('row-threshold', 'value'),
         Input('column-threshold', 'value'),
         Input('selected-rows', 'value'),
         Input('selected-columns', 'value')],
        state=[State('file-upload', 'contents')]
    )
    def compute_traces_once(
            filename, cluster,
            rowThresh, colThresh,
            selRows, selCols,
            contents):

        global computedTraces
        
        if(len(selRows) < 2 or len(selCols) < 2):
            return []
        
        # load default data if no file has been uploaded
        if(contents is None and filename is not None):
            data, _, _, _ = geneExpressionReader.parse_tsv(
                filepath=filename,
                rowLabelsSource='Gene Name',
                rows=selRows,
                columns=selCols
            )
        else:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('UTF-8')

            data, _, _, _ = \
                geneExpressionReader.parse_tsv(
                    contents=decoded,
                    rowLabelsSource='Gene Name',
                    rows=selRows, columns=selCols
                )

        if(len(data) == 0):
            return []

        fig_options.update(
            data=data,
            columnLabels=selCols,
            rowLabels=selRows,
            colorThreshold=dict(row=rowThresh, col=colThresh),
        )

        if(len(cluster) > 1):
            fig_options.update(
                cluster='all'
            )
        else:
            fig_options.update(
                cluster=cluster[0]
            )

        (_, computed_traces) = dash_bio.ClustergramComponent(
            **fig_options
        )
        return ['calculated']
    
