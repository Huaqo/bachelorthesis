from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum)
from qgis import processing

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class matplotlibBar(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    ATTRIBUTE_CAT = 'ATTRIBUTE_CAT'
    ATTRIBUTE_VAL = 'ATTRIBUTE_VAL'
    SORTING_OPTION = 'SORTING_OPTION'
    ATTRIBUTE_COLOR = 'ATTRIBUTE_COLOR'
    COLOR_MAP = 'COLOR_MAP'
    SHOW_LEGEND = 'SHOW_LEGEND'
    LEGEND_TITLE = 'LEGEND_TITLE'
    PLOT_OUTPUT = 'PLOT_OUTPUT'
    FIG_WIDTH = 'FIG_WIDTH'
    FIG_HEIGHT = 'FIG_HEIGHT'
    ALPHA = 'ALPHA'
    COLOR = 'COLOR'
    SHOW_GRID = 'SHOW_GRID'
    PLOT_TITLE = 'PLOT_TITLE'
    X_LABEL = 'X_LABEL'
    Y_LABEL = 'Y_LABEL'
    X_TICK_ROTATION = 'X_TICK_ROTATION'
    X_TICK_ALIGNMENT = 'X_TICK_ALIGNMENT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return matplotlibBar()

    def name(self):
        return 'Bar Plot'

    def displayName(self):
        return self.tr('Bar Plot')

    def group(self):
        return self.tr('matplotlib vector')

    def groupId(self):
        return 'matplotlib vector'

    def shortHelpString(self):
        return self.tr("Generates a Bar Plot for a category attribute and a value attribute and colors them depending another attribute from an input layer.")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr('Input layer'),
            [QgsProcessing.TypeVectorAnyGeometry]
        )
        )
        self.addParameter(QgsProcessingParameterField(
            self.ATTRIBUTE_CAT,
            self.tr('Category Attribute'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Any
        )
        )
        self.addParameter(QgsProcessingParameterField(
            self.ATTRIBUTE_VAL,
            self.tr('Value Attribute'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric
        )
        )

        sorting_options = [
            ('NO_SORTING', ('No Sorting')),
            ('ASCENDING', ('Ascending')),
            ('DESCENDING', ('Descending'))
        ]

        self.addParameter(QgsProcessingParameterEnum(
            self.SORTING_OPTION,
            self.tr('Sorting Option'),
            options=[option[1] for option in sorting_options],
            defaultValue=0,
            allowMultiple=False
        )
        )

        self.addParameter(QgsProcessingParameterFileDestination(
            'PLOT_OUTPUT',
            self.tr('Plot Output File'),
            'PNG Files (*.png)'
        )
        )
        self.addParameter(QgsProcessingParameterNumber(
            self.FIG_WIDTH,
            self.tr('Figure Width'),
            QgsProcessingParameterNumber.Double,
            10
        )
        )
        self.addParameter(QgsProcessingParameterNumber(
            self.FIG_HEIGHT,
            self.tr('Figure Height'),
            QgsProcessingParameterNumber.Double,
            6
        )
        )
        self.addParameter(QgsProcessingParameterNumber(
            self.ALPHA,
            self.tr('Alpha Transparency'),
            QgsProcessingParameterNumber.Double,
            0.7
        )
        )
        self.addParameter(QgsProcessingParameterString(
            self.COLOR,
            self.tr('Color'),
            defaultValue='blue'
        )
        )
        self.addParameter(QgsProcessingParameterBoolean(
            self.SHOW_GRID,
            self.tr('Show Grid'),
            defaultValue=True
        )
        )
        self.addParameter(QgsProcessingParameterString(
            self.PLOT_TITLE,
            self.tr('Plot Title'),
            defaultValue=' '
        )
        )
        self.addParameter(QgsProcessingParameterString(
            self.X_LABEL,
            self.tr('X-axis Label (Categories)'),
            defaultValue=' '
        )
        )
        self.addParameter(QgsProcessingParameterString(
            self.Y_LABEL,
            self.tr('Y-axis Label (Values)'),
            defaultValue=' '
        )
        )
        self.addParameter(QgsProcessingParameterNumber(
            self.X_TICK_ROTATION,
            self.tr('X-axis Tick Label Rotation'),
            QgsProcessingParameterNumber.Integer,
            defaultValue=45
        )
        )
        self.addParameter(QgsProcessingParameterString(
            self.X_TICK_ALIGNMENT,
            self.tr('X-axis Tick Label Alignment'),
            defaultValue='right'
        )
        )
        self.addParameter(QgsProcessingParameterField(
            self.ATTRIBUTE_COLOR,
            self.tr('Color Attribute'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Any,
            optional=True
        )
        )

        self.addParameter(QgsProcessingParameterString(
            self.COLOR_MAP,
            self.tr('Color Map'),
            defaultValue='viridis',
        )
        )

        self.addParameter(QgsProcessingParameterBoolean(
            'SHOW_LEGEND',
            self.tr('Show Legend'),
            defaultValue=True,
        )
        )

        self.addParameter(QgsProcessingParameterString(
            self.LEGEND_TITLE,
            self.tr('Legend Title'),
            optional=True,
            defaultValue=' '
        )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        cat_attribute_name = self.parameterAsString(
            parameters, self.ATTRIBUTE_CAT, context)
        val_attribute_name = self.parameterAsString(
            parameters, self.ATTRIBUTE_VAL, context)
        color_attribute_name = self.parameterAsString(
            parameters, self.ATTRIBUTE_COLOR, context)
        color_map_name = self.parameterAsString(
            parameters, self.COLOR_MAP, context)
        plot_output_path = self.parameterAsFileOutput(
            parameters, 'PLOT_OUTPUT', context)
        fig_width = self.parameterAsDouble(parameters, self.FIG_WIDTH, context)
        fig_height = self.parameterAsDouble(
            parameters, self.FIG_HEIGHT, context)
        alpha = self.parameterAsDouble(parameters, self.ALPHA, context)
        color = self.parameterAsString(parameters, self.COLOR, context)
        show_grid = self.parameterAsBool(parameters, self.SHOW_GRID, context)
        plot_title = self.parameterAsString(
            parameters, self.PLOT_TITLE, context)
        x_label = self.parameterAsString(parameters, self.X_LABEL, context)
        y_label = self.parameterAsString(parameters, self.Y_LABEL, context)
        x_tick_rotation = self.parameterAsInt(
            parameters, self.X_TICK_ROTATION, context)
        x_tick_alignment = self.parameterAsString(
            parameters, self.X_TICK_ALIGNMENT, context)
        show_legend = self.parameterAsBool(parameters, self.SHOW_LEGEND, context)
        legend_title = self.parameterAsString(
            parameters, self.LEGEND_TITLE, context)
        sorting_option = self.parameterAsEnum(
            parameters, self.SORTING_OPTION, context)

        categories, values, color_values = [], [], []

        for feature in source.getFeatures():
            cat_value = feature[cat_attribute_name]
            val_value = feature[val_attribute_name]

            if cat_value is not None and val_value is not None:
                categories.append(str(cat_value))
                values.append(float(val_value))

            if color_attribute_name:
                color_value = feature[color_attribute_name] if feature[color_attribute_name] is not None else "Default"
                color_values.append(color_value)

        if sorting_option == 1:
            sorted_indices = sorted(
                range(len(values)), key=lambda i: values[i])
        elif sorting_option == 2:
            sorted_indices = sorted(
                range(len(values)), key=lambda i: values[i], reverse=True)
        else:
            sorted_indices = range(len(values))

        sorted_categories = [categories[i] for i in sorted_indices]
        sorted_values = [values[i] for i in sorted_indices]

        if color_attribute_name:
            color_values = [color_values[i] for i in sorted_indices]

        plt.figure(figsize=(fig_width, fig_height))

        if color_attribute_name:
            unique_colors = list(set(color_values))
            colormap = plt.cm.get_cmap(color_map_name, len(unique_colors))
            norm = Normalize(vmin=0, vmax=len(unique_colors)-1)
            color_map = {color: colormap(norm(i))
                         for i, color in enumerate(unique_colors)}
            bar_colors = [color_map[value] for value in color_values]

            for i, (cat, val) in enumerate(zip(sorted_categories, sorted_values)):
                plt.bar(cat, val, color=bar_colors[i], label=color_values[i]
                        if i == 0 or color_values[i] != color_values[i-1] else "")
            if show_legend:
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys(), title=legend_title)

        else:
            plt.bar(sorted_categories, sorted_values, color=color, alpha=alpha)

        if color_attribute_name and len(color_values) != len(categories):
            raise QgsProcessingException(
                self.tr('Mismatch in the number of categories and color values.'))

        if not categories or not values:
            raise QgsProcessingException(
                self.tr("No valid data found. Please check the selected attributes."))

        if not legend_title.strip():
            legend_title = color_attribute_name if color_attribute_name else 'Legend'

        plt.title(plot_title if plot_title else 'Value Distribution by Category')
        plt.xlabel(x_label if x_label else 'Category')
        plt.ylabel(y_label if y_label else 'Value')

        if show_grid:
            plt.grid(True)
        else:
            plt.grid(False)

        plt.xticks(rotation=x_tick_rotation, ha=x_tick_alignment)
        plt.tight_layout()

        try:
            plt.savefig(plot_output_path)
            plt.close()
            return {}
        except Exception as e:
            feedback.reportError(str(e))
            return {}
