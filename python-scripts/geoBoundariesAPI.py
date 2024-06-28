from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsFeature,
                       QgsField,
                       QgsGeometry,
                       QgsVectorLayer,
                       QgsProject,
                       QgsProcessingContext)
from qgis import processing
import requests
import geopandas as gpd

class FetchGeoBoundaryAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    RELEASE_TYPE = 'RELEASE_TYPE'
    COUNTRY_CODE = 'COUNTRY_CODE'
    BOUNDARY_TYPE = 'BOUNDARY_TYPE'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FetchGeoBoundaryAlgorithm()

    def name(self):
        return 'fetchgeoboundary'

    def displayName(self):
        return self.tr('Fetch geoBoundaries')

    def group(self):
        return self.tr('geoBoundaries')

    def groupId(self):
        return 'geoboundaryscripts'

    def shortHelpString(self):
        return self.tr("Fetches geoBoundaries and adds them. This is an unofficial tool by Joaquin Gottlebe. \n More information: https://www.geoboundaries.org/index.html")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                self.COUNTRY_CODE,
                self.tr('Country Code ISO-3'),
                defaultValue='DEU'
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.BOUNDARY_TYPE,
                self.tr('Boundary Type'),
                options=['ADM0','ADM1','ADM2','ADM3','ADM4','ADM5'],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.RELEASE_TYPE,
                self.tr('Release Type'),
                options=['gbOpen','gbHumanitarian','gbAuthorative'],
                defaultValue='gbOpen'
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        
        release_type_index = self.parameterAsEnum(parameters, self.RELEASE_TYPE, context)
        release_types = ['gbOpen', 'gbHumanitarian', 'gbAuthorative']
        release_type = release_types[release_type_index]
        
        country_code = self.parameterAsString(parameters, self.COUNTRY_CODE, context)
        
        boundary_type_index = self.parameterAsEnum(parameters, self.BOUNDARY_TYPE, context)
        boundary_types = ['ADM0','ADM1','ADM2','ADM3','ADM4','ADM5']
        boundary_type = boundary_types[boundary_type_index]

        results = self.fetch_geoboundary(release_type, country_code, boundary_type, feedback)

        if not results:
            raise QgsProcessingException('Failed to fetch geoBoundary')
        
        total_features = sum(len(result['gdf']) for result in results)
        processed_features = 0
        
        layer_name = f"{country_code}_{boundary_type}_{release_type}_geoBoundaries"
        vector_layer = QgsVectorLayer("Polygon?crs=epsg:4326", layer_name, "memory")
        pr = vector_layer.dataProvider()
        
        for result in results:
            gdf = result['gdf']
            metadata = result['metadata']

            if gdf.empty:
                feedback.reportError("Loaded GeoDataFrame is empty.")
                continue

            for index, row in gdf.iterrows():
                if feedback.isCanceled():
                    break

                # Debugging type and attribute
                if not hasattr(row['geometry'], 'wkt'):
                    feedback.reportError(f"Unexpected type for geometry: {type(row['geometry'])}. Expected shapely geometry object.")
                    continue  # Skip this iteration if the geometry type is unexpected

                # Assuming row['geometry'] is a shapely.geometry object as expected
                feat = QgsFeature()
                try:
                    feat.setGeometry(QgsGeometry.fromWkt(row['geometry'].wkt))
                except Exception as e:
                    feedback.reportError(f"Error setting geometry from WKT: {e}")
                    continue  # Skip this iteration if there was an error setting the geometry

                # Add additional feature settings and add feature to the provider as necessary
                pr.addFeature(feat)

        vector_layer.updateExtents()
        
        QgsProject.instance().addMapLayer(vector_layer)

        feedback.pushInfo("GeoBoundary layer added to the project.")
        
        return {self.OUTPUT: vector_layer.id()}

    def fetch_geoboundary(self, release_type, country_code, boundary_type, feedback):
        api_url = f"https://www.geoboundaries.org/api/current/{release_type}/{country_code}/{boundary_type}/"
        try:
            response = requests.get(api_url)
            if response.status_code != 200:
                print(f"Failed to fetch data: HTTP Status Code {response.status_code}")
                return None

            data = response.json()
            results = []
            
            if not isinstance(data, list):
                data = [data]
                
            total_countries = len(data)
            processed_countries = 0
            
            for country_data in data:
                
                if feedback.isCanceled():
                    return None
                
                if 'gjDownloadURL' not in country_data:
                    feedback.reportError("'gjDownloadURL' not found in the response for" + country_data.get('boundaryISO', 'an unknown country'))
                    continue

                geojson_url = country_data['gjDownloadURL']
                gdf = gpd.read_file(geojson_url)
                if gdf.empty:
                    feedback.reportError("Loaded GeoDataFrame is empty.")
                    continue
                    
                metadata = {key: country_data.get(key, '') for key in country_data}
                
                results.append({'gdf': gdf, 'metadata' : metadata})
                
                processed_countries += 1
                feedback.setProgress(int((processed_countries / total_countries) * 100))
                

            return results
            
        except requests.RequestException as e:
            feedback.reportError(f"Request error: {e}")
        except Exception as e:
            feedback.reportError(f"An unexpected error occurred: {e}")

        return None