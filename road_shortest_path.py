from math import hypot
import heapq

from qgis.PyQt.QtCore import QVariant, Qt, QSettings
from qgis.PyQt.QtGui import QColor, QCursor, QPixmap, QPainter, QPen
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QToolBar, QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
from qgis.core import (
    QgsProject,
    QgsMapLayerType,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsField,
    QgsSymbol,
    QgsMarkerSymbol,
    QgsSimpleMarkerSymbolLayer,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsSettings,
    QgsSpatialIndex,
)
from qgis.gui import QgsMapToolEmitPoint

DEFAULT_ROUTE_COLOR = '#ff0000'
SETTINGS_PREFIX = 'RoadShortestPath'

TRANSLATIONS = {
    'en': {
        'route': 'Route', 'clear_route': 'Clear route', 'roads_layer': 'Road layer:',
        'choose_line_layer': 'Select a road line layer.', 'click_start': 'Click the start point.',
        'click_end': 'Click the new destination point. Start remains fixed.',
        'start_selected': 'Start selected. Now click the destination point.',
        'cleared': 'Route and points cleared. Select a new start point.',
        'graph_failed': 'Failed to build a road graph from the selected layer.',
        'nearest_failed': 'Could not find the nearest graph vertices.',
        'route_not_found': 'No route found between the selected points.',
        'route_updated': 'Route updated from the fixed start point to the new destination.',
        'route_layer': 'Route', 'marker_layer': 'Route points', 'start': 'Start', 'end': 'End',
        'shortest_path': 'Shortest path', 'menu': 'Road Shortest Path', 'caching': 'Caching…'
    },
    'ru': {
        'route': 'Маршрут', 'clear_route': 'Очистить маршрут', 'roads_layer': 'Слой дорог:',
        'choose_line_layer': 'Выберите линейный слой дорог.', 'click_start': 'Щелкните стартовую точку.',
        'click_end': 'Щелкните новую конечную точку. Старт сохраняется.',
        'start_selected': 'Старт выбран. Теперь щелкните финишную точку.',
        'cleared': 'Маршрут и точки очищены. Выберите новый старт.',
        'graph_failed': 'Не удалось построить граф дорог из выбранного слоя.',
        'nearest_failed': 'Не найдены ближайшие вершины графа.',
        'route_not_found': 'Маршрут между выбранными точками не найден.',
        'route_updated': 'Маршрут обновлен от фиксированного старта к новой конечной точке.',
        'route_layer': 'Маршрут', 'marker_layer': 'Точки маршрута', 'start': 'Старт', 'end': 'Финиш',
        'shortest_path': 'Кратчайший путь', 'menu': 'Поиск кратчайшего пути', 'caching': 'Кэширование…'
    },
    'uk': {
        'route': 'Маршрут', 'clear_route': 'Очистити маршрут', 'roads_layer': 'Шар доріг:',
        'choose_line_layer': 'Виберіть лінійний шар доріг.', 'click_start': 'Клацніть стартову точку.',
        'click_end': 'Клацніть нову кінцеву точку. Старт залишається фіксованим.',
        'start_selected': 'Старт вибрано. Тепер клацніть кінцеву точку.',
        'cleared': 'Маршрут і точки очищено. Виберіть новий старт.',
        'graph_failed': 'Не вдалося побудувати граф доріг з вибраного шару.',
        'nearest_failed': 'Не знайдено найближчі вершини графа.',
        'route_not_found': 'Маршрут між вибраними точками не знайдено.',
        'route_updated': 'Маршрут оновлено від фіксованого старту до нової кінцевої точки.',
        'route_layer': 'Маршрут', 'marker_layer': 'Точки маршруту', 'start': 'Старт', 'end': 'Фініш',
        'shortest_path': 'Найкоротший шлях', 'menu': 'Пошук найкоротшого шляху', 'caching': 'Кешування…'
    },
    'pl': {
        'route': 'Trasa', 'clear_route': 'Wyczyść trasę', 'roads_layer': 'Warstwa dróg:',
        'choose_line_layer': 'Wybierz liniową warstwę dróg.', 'click_start': 'Kliknij punkt startowy.',
        'click_end': 'Kliknij nowy punkt końcowy. Start pozostaje stały.',
        'start_selected': 'Wybrano start. Teraz kliknij punkt końcowy.',
        'cleared': 'Trasa i punkty zostały wyczyszczone. Wybierz nowy punkt startowy.',
        'graph_failed': 'Nie udało się zbudować grafu dróg z wybranej warstwy.',
        'nearest_failed': 'Nie znaleziono najbliższych wierzchołków grafu.',
        'route_not_found': 'Nie znaleziono trasy między wybranymi punktami.',
        'route_updated': 'Trasa została zaktualizowana od stałego punktu startowego do nowego celu.',
        'route_layer': 'Trasa', 'marker_layer': 'Punkty trasy', 'start': 'Start', 'end': 'Koniec',
        'shortest_path': 'Najkrótsza trasa', 'menu': 'Najkrótsza trasa drogowa', 'caching': 'Buforowanie…'
    },
    'fr': {
        'route': 'Itinéraire', 'clear_route': 'Effacer l’itinéraire', 'roads_layer': 'Couche de routes :',
        'choose_line_layer': 'Sélectionnez une couche linéaire de routes.', 'click_start': 'Cliquez sur le point de départ.',
        'click_end': 'Cliquez sur le nouveau point d’arrivée. Le départ reste fixe.',
        'start_selected': 'Départ sélectionné. Cliquez maintenant sur le point d’arrivée.',
        'cleared': 'Itinéraire et points effacés. Sélectionnez un nouveau départ.',
        'graph_failed': 'Impossible de construire un graphe routier à partir de la couche sélectionnée.',
        'nearest_failed': 'Impossible de trouver les sommets du graphe les plus proches.',
        'route_not_found': 'Aucun itinéraire trouvé entre les points sélectionnés.',
        'route_updated': 'Itinéraire mis à jour depuis le départ fixe vers la nouvelle destination.',
        'route_layer': 'Itinéraire', 'marker_layer': 'Points d’itinéraire', 'start': 'Départ', 'end': 'Arrivée',
        'shortest_path': 'Chemin le plus court', 'menu': 'Plus court chemin routier', 'caching': 'Mise en cache…'
    },
    'ka': {
        'route': 'მარშრუტი', 'clear_route': 'მარშრუტის გასუფთავება', 'roads_layer': 'გზების ფენა:',
        'choose_line_layer': 'აირჩიეთ გზების ხაზოვანი ფენა.', 'click_start': 'დააწკაპუნეთ საწყის წერტილზე.',
        'click_end': 'დააწკაპუნეთ ახალ საბოლოო წერტილზე. საწყისი ფიქსირებულია.',
        'start_selected': 'საწყისი არჩეულია. ახლა დააწკაპუნეთ საბოლოო წერტილზე.',
        'cleared': 'მარშრუტი და წერტილები გასუფთავდა. აირჩიეთ ახალი საწყისი წერტილი.',
        'graph_failed': 'არჩეული ფენიდან გზების გრაფის აგება ვერ მოხერხდა.',
        'nearest_failed': 'გრაფის უახლოესი წვეროები ვერ მოიძებნა.',
        'route_not_found': 'არჩეულ წერტილებს შორის მარშრუტი ვერ მოიძებნა.',
        'route_updated': 'მარშრუტი განახლდა ფიქსირებული საწყისიდან ახალ საბოლოო წერტილამდე.',
        'route_layer': 'მარშრუტი', 'marker_layer': 'მარშრუტის წერტილები', 'start': 'საწყისი', 'end': 'ფინიში',
        'shortest_path': 'უმოკლესი გზა', 'menu': 'გზებზე უმოკლესი გზა', 'caching': 'ქეშირება…'
    },
    'az': {
        'route': 'Marşrut', 'clear_route': 'Marşrutu təmizlə', 'roads_layer': 'Yol qatı:',
        'choose_line_layer': 'Yollar üçün xətti qat seçin.', 'click_start': 'Başlanğıc nöqtəni seçin.',
        'click_end': 'Yeni son nöqtəni seçin. Başlanğıc sabit qalır.',
        'start_selected': 'Başlanğıc seçildi. İndi son nöqtəni seçin.',
        'cleared': 'Marşrut və nöqtələr təmizləndi. Yeni başlanğıc nöqtəsi seçin.',
        'graph_failed': 'Seçilmiş qatdan yol qrafını qurmaq mümkün olmadı.',
        'nearest_failed': 'Qrafın ən yaxın zirvələri tapılmadı.',
        'route_not_found': 'Seçilmiş nöqtələr arasında marşrut tapılmadı.',
        'route_updated': 'Marşrut sabit başlanğıcdan yeni son nöqtəyə qədər yeniləndi.',
        'route_layer': 'Marşrut', 'marker_layer': 'Marşrut nöqtələri', 'start': 'Başlanğıc', 'end': 'Son',
        'shortest_path': 'Ən qısa yol', 'menu': 'Yolda ən qısa yol', 'caching': 'Keşləmə…'
    },
}

class PointPickerTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.canvas = canvas
        self.callback = callback
        self.setCursor(self._build_target_cursor())

    def _build_target_cursor(self):
        size = 32
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        c = size // 2
        painter.drawLine(c, 2, c, 11)
        painter.drawLine(c, 21, c, size - 3)
        painter.drawLine(2, c, 11, c)
        painter.drawLine(21, c, size - 3, c)
        painter.drawEllipse(c - 5, c - 5, 10, 10)
        pen2 = QPen(QColor(255, 255, 255))
        pen2.setWidth(1)
        painter.setPen(pen2)
        painter.drawEllipse(c - 2, c - 2, 4, 4)
        painter.end()
        return QCursor(pix, c, c)

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.callback(point)

class RoadShortestPathPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.clear_action = None
        self.toolbar = None
        self.selector_widget = None
        self.layer_combo = None
        self.layer_label = None
        self.color_button = None
        self.map_tool = None
        self.previous_map_tool = None
        self.start_point = None
        self.end_point = None
        self.route_layer = None
        self.route_layer_id = None
        self.marker_layer_id = None
        self.locale = self.detect_locale()
        self.route_color = DEFAULT_ROUTE_COLOR
        self.settings = QgsSettings()
        self.graph_cache = None
        self.start_key = None
        self.start_overrides = None
        self.layer_choice_restored = False

    def detect_locale(self):
        locale = QSettings().value('locale/userLocale', 'en')
        if not locale:
            return 'en'
        locale = str(locale)[:2].lower()
        return locale if locale in TRANSLATIONS else 'en'

    def tr(self, key):
        return TRANSLATIONS.get(self.locale, TRANSLATIONS['en']).get(key, key)

    def setting_key(self, name):
        return f'{SETTINGS_PREFIX}/{name}'

    def load_settings(self):
        self.route_color = self.settings.value(self.setting_key('route_color'), DEFAULT_ROUTE_COLOR)
        x = self.settings.value(self.setting_key('start_x'), None)
        y = self.settings.value(self.setting_key('start_y'), None)
        if x is not None and y is not None:
            try:
                self.start_point = QgsPointXY(float(x), float(y))
            except Exception:
                self.start_point = None

    def save_settings(self):
        if self.layer_combo is not None:
            layer_id = self.layer_combo.currentData()
            layer = QgsProject.instance().mapLayer(layer_id) if layer_id else None
            self.settings.setValue(self.setting_key('selected_layer_name'), layer.name() if layer else '')
            self.settings.setValue(self.setting_key('selected_layer_source'), layer.source() if layer else '')
        self.settings.setValue(self.setting_key('route_color'), self.route_color)
        if self.start_point is not None:
            self.settings.setValue(self.setting_key('start_x'), self.start_point.x())
            self.settings.setValue(self.setting_key('start_y'), self.start_point.y())
        else:
            self.settings.remove(self.setting_key('start_x'))
            self.settings.remove(self.setting_key('start_y'))

    def restore_toolbar_state(self):
        state = self.settings.value(self.setting_key('toolbar_visible'), True, type=bool)
        if self.toolbar is not None:
            self.toolbar.setVisible(state)

    def initGui(self):
        self.load_settings()
        self.action = QAction(self.tr('route'), self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.toggled.connect(self.on_route_toggled)
        self.iface.addPluginToMenu(self.tr('menu'), self.action)

        self.clear_action = QAction(self.tr('clear_route'), self.iface.mainWindow())
        self.clear_action.triggered.connect(self.clear_selection)
        self.iface.addPluginToMenu(self.tr('menu'), self.clear_action)

        self.toolbar = self.iface.addToolBar('RoadShortestPathToolbar')
        self.toolbar.setObjectName('RoadShortestPathToolbar')
        self.toolbar.setWindowTitle(self.tr('menu'))
        self.toolbar.addAction(self.action)
        self.toolbar.addAction(self.clear_action)

        self.selector_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 0, 4, 0)
        self.layer_label = QLabel(self.tr('roads_layer'))
        layout.addWidget(self.layer_label)
        self.layer_combo = QComboBox()
        self.layer_combo.setMinimumWidth(220)
        self.layer_combo.currentIndexChanged.connect(self.on_layer_changed)
        layout.addWidget(self.layer_combo)
        self.color_button = QPushButton('●')
        self.color_button.setToolTip('Route color')
        self.color_button.setMaximumWidth(28)
        self.color_button.clicked.connect(self.cycle_route_color)
        self.update_color_button()
        layout.addWidget(self.color_button)
        self.selector_widget.setLayout(layout)
        self.toolbar.addWidget(self.selector_widget)

        self.refresh_layer_list()
        self.restore_toolbar_state()
        if self.start_point is not None and self.selected_layer() is not None:
            try:
                self.update_marker_layer(start_point=self.start_point, end_point=None)
            except Exception:
                self.start_point = None
        self.canvas.mapToolSet.connect(self.on_map_tool_changed)
        QgsProject.instance().layersAdded.connect(self.refresh_layer_list)
        QgsProject.instance().layersRemoved.connect(self.refresh_layer_list)

    def update_color_button(self):
        if self.color_button is not None:
            self.color_button.setStyleSheet(f'color: {self.route_color}; font-weight: bold;')

    def cycle_route_color(self):
        colors = ['#ff0000', '#0066ff', '#00aa55', '#ff8800', '#aa00ff']
        idx = colors.index(self.route_color) if self.route_color in colors else 0
        self.route_color = colors[(idx + 1) % len(colors)]
        self.update_color_button()
        self.save_settings()
        if self.route_layer_id:
            self.update_route_style()
        if self.marker_layer_id:
            self.update_marker_style()

    def on_layer_changed(self):
        self.clear_selection()
        self.save_settings()
        if self.action is not None and self.action.isChecked():
            self.activate_route_mode(show_message=True)


    def unload(self):
        self.save_settings()
        if self.toolbar is not None:
            self.settings.setValue(self.setting_key('toolbar_visible'), self.toolbar.isVisible())
        if self.map_tool and self.canvas.mapTool() == self.map_tool and self.previous_map_tool:
            self.canvas.setMapTool(self.previous_map_tool)
        self.canvas.mapToolSet.disconnect(self.on_map_tool_changed)
        QgsProject.instance().layersAdded.disconnect(self.refresh_layer_list)
        QgsProject.instance().layersRemoved.disconnect(self.refresh_layer_list)
        if self.action is not None:
            self.iface.removePluginMenu(self.tr('menu'), self.action)
        if self.clear_action is not None:
            self.iface.removePluginMenu(self.tr('menu'), self.clear_action)
        if self.toolbar is not None:
            self.iface.mainWindow().removeToolBar(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None

    def refresh_layer_list(self, *args):
        if self.layer_combo is None:
            return
        current_id = self.layer_combo.currentData()
        current_layer = QgsProject.instance().mapLayer(current_id) if current_id else None
        current_name = current_layer.name() if current_layer else None
        current_source = current_layer.source() if current_layer else None

        self.layer_combo.blockSignals(True)
        self.layer_combo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayerType.VectorLayer and layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.layer_combo.addItem(layer.name(), layer.id())

        restored_idx = -1
        if current_source or current_name:
            for i in range(self.layer_combo.count()):
                layer = QgsProject.instance().mapLayer(self.layer_combo.itemData(i))
                if layer is None:
                    continue
                if current_source and layer.source() == current_source:
                    restored_idx = i
                    break
                if current_name and layer.name() == current_name and restored_idx < 0:
                    restored_idx = i

        if restored_idx >= 0:
            self.layer_combo.setCurrentIndex(restored_idx)
        elif not self.layer_choice_restored:
            self.apply_layer_selection_priority()

        self.layer_combo.blockSignals(False)
        self.update_toolbar_enabled_state()

    def apply_layer_selection_priority(self):
        """Priority: previously saved layer (by source/name) -> layer named 'Road.shp' -> first in list."""
        if self.layer_combo is None or self.layer_combo.count() == 0:
            return

        saved_name = self.settings.value(self.setting_key('selected_layer_name'), '')
        saved_source = self.settings.value(self.setting_key('selected_layer_source'), '')
        chosen_idx = -1

        if saved_source or saved_name:
            for i in range(self.layer_combo.count()):
                layer = QgsProject.instance().mapLayer(self.layer_combo.itemData(i))
                if layer is None:
                    continue
                if saved_source and layer.source() == saved_source:
                    chosen_idx = i
                    break
                if saved_name and layer.name() == saved_name and chosen_idx < 0:
                    chosen_idx = i

        if chosen_idx < 0:
            road_idx = self.layer_combo.findText('Road.shp')
            if road_idx >= 0:
                chosen_idx = road_idx

        if chosen_idx < 0:
            chosen_idx = 0

        self.layer_combo.setCurrentIndex(chosen_idx)
        self.layer_choice_restored = True

    def update_toolbar_enabled_state(self):
        has_layers = self.layer_combo is not None and self.layer_combo.count() > 0
        if self.action is not None:
            self.action.setEnabled(has_layers)
        if self.clear_action is not None:
            self.clear_action.setEnabled(has_layers)
        if self.color_button is not None:
            self.color_button.setEnabled(has_layers)
        if not has_layers and self.action is not None and self.action.isChecked():
            self.action.setChecked(False)

    def selected_layer(self):
        layer_id = self.layer_combo.currentData()
        if not layer_id:
            return None
        return QgsProject.instance().mapLayer(layer_id)

    def on_route_toggled(self, checked):
        if checked:
            self.activate_route_mode(show_message=True)
        else:
            self.deactivate_route_mode()

    def activate_route_mode(self, show_message=False):
        layer = self.selected_layer()
        if not layer:
            if show_message:
                QMessageBox.warning(self.iface.mainWindow(), self.tr('route'), self.tr('choose_line_layer'))
            if self.action is not None:
                self.action.blockSignals(True)
                self.action.setChecked(False)
                self.action.blockSignals(False)
            return
        self.get_cached_graph(layer)
        self.previous_map_tool = self.canvas.mapTool()
        self.map_tool = PointPickerTool(self.canvas, self.handle_map_click)
        self.canvas.setMapTool(self.map_tool)
        if self.action is not None:
            self.action.blockSignals(True)
            self.action.setChecked(True)
            self.action.blockSignals(False)
        if show_message:
            if self.start_point is None:
                self.iface.messageBar().pushMessage(self.tr('route'), self.tr('click_start'), level=0, duration=4)
            else:
                self.iface.messageBar().pushMessage(self.tr('route'), self.tr('click_end'), level=0, duration=4)

    def deactivate_route_mode(self):
        if self.map_tool and self.canvas.mapTool() == self.map_tool:
            if self.previous_map_tool:
                self.canvas.setMapTool(self.previous_map_tool)
            else:
                self.canvas.unsetMapTool(self.map_tool)
        self.map_tool = None
        if self.action is not None:
            self.action.blockSignals(True)
            self.action.setChecked(False)
            self.action.blockSignals(False)

    def on_map_tool_changed(self, new_tool, old_tool):
        if self.map_tool is not None and new_tool != self.map_tool:
            self.map_tool = None
            if self.action is not None:
                self.action.blockSignals(True)
                self.action.setChecked(False)
                self.action.blockSignals(False)

    def clear_selection(self):
        self.start_point = None
        self.end_point = None
        self.clear_route_layer()
        self.clear_marker_layer()
        self.save_settings()
        self.iface.messageBar().pushMessage(self.tr('route'), self.tr('cleared'), level=0, duration=3)

    def handle_map_click(self, point):
        if self.action is None or not self.action.isChecked():
            return
        if self.start_point is None:
            self.start_point = point
            self.end_point = None
            self.save_settings()
            self.update_marker_layer(start_point=self.start_point, end_point=None)
            self.iface.messageBar().pushMessage(self.tr('route'), self.tr('start_selected'), level=0, duration=3)
            return
        self.end_point = point
        self.update_marker_layer(start_point=self.start_point, end_point=self.end_point)
        self.build_route()

    def build_graph(self, layer):
        graph = {}
        point_lookup = {}
        edge_layer = QgsVectorLayer(f'LineString?crs={layer.crs().authid()}', 'edges', 'memory')
        edge_provider = edge_layer.dataProvider()
        edge_provider.addAttributes([QgsField('k1x', QVariant.Double), QgsField('k1y', QVariant.Double),
                                      QgsField('k2x', QVariant.Double), QgsField('k2y', QVariant.Double)])
        edge_layer.updateFields()
        edge_features = []
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if geom.isEmpty():
                continue
            lines = geom.asMultiPolyline() if geom.isMultipart() else [geom.asPolyline()]
            for line in lines:
                if len(line) < 2:
                    continue
                for i in range(len(line) - 1):
                    p1 = QgsPointXY(line[i])
                    p2 = QgsPointXY(line[i + 1])
                    k1 = self.point_key(p1)
                    k2 = self.point_key(p2)
                    point_lookup[k1] = p1
                    point_lookup[k2] = p2
                    dist = self.distance(p1, p2)
                    if dist <= 0:
                        continue
                    graph.setdefault(k1, []).append((k2, dist))
                    graph.setdefault(k2, []).append((k1, dist))
                    ef = QgsFeature(edge_layer.fields())
                    ef.setGeometry(QgsGeometry.fromPolylineXY([p1, p2]))
                    ef.setAttributes([k1[0], k1[1], k2[0], k2[1]])
                    edge_features.append(ef)
        if edge_features:
            edge_provider.addFeatures(edge_features)
        edge_layer.updateExtents()
        spatial_index = QgsSpatialIndex(edge_layer.getFeatures())
        return graph, point_lookup, edge_layer, spatial_index

    def get_cached_graph(self, layer):
        key = (layer.id(), layer.featureCount())
        if self.graph_cache and self.graph_cache.get('key') == key:
            return self.graph_cache
        self.iface.messageBar().pushMessage(self.tr('route'), self.tr('caching'), level=0, duration=0)
        from qgis.PyQt.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            graph, point_lookup, edge_layer, spatial_index = self.build_graph(layer)
        finally:
            self.iface.messageBar().clearWidgets()
        self.graph_cache = {
            'key': key,
            'graph': graph,
            'point_lookup': point_lookup,
            'edge_layer': edge_layer,
            'spatial_index': spatial_index,
            'dijkstra_from': None,
            'dijkstra_start_key': None,
        }
        return self.graph_cache

    def snap_to_graph(self, target_point, cache):
        graph = cache['graph']
        point_lookup = cache['point_lookup']
        edge_layer = cache['edge_layer']
        spatial_index = cache['spatial_index']
        candidate_ids = spatial_index.nearestNeighbor(target_point, 5)
        if not candidate_ids:
            return None, None
        best_dist = float('inf')
        best_point = None
        best_k1 = None
        best_k2 = None
        for fid in candidate_ids:
            feat = edge_layer.getFeature(fid)
            geom = feat.geometry()
            result = geom.closestSegmentWithContext(target_point)
            sqr_dist, proj_point = result[0], result[1]
            if sqr_dist < best_dist:
                best_dist = sqr_dist
                best_point = QgsPointXY(proj_point)
                best_k1 = (feat['k1x'], feat['k1y'])
                best_k2 = (feat['k2x'], feat['k2y'])
        if best_point is None:
            return None, None
        virtual_key = ('v', round(best_point.x(), 6), round(best_point.y(), 6), best_k1, best_k2)
        point_lookup[virtual_key] = best_point
        p1 = point_lookup.get(best_k1)
        p2 = point_lookup.get(best_k2)
        w1 = self.distance(best_point, p1) if p1 else float('inf')
        w2 = self.distance(best_point, p2) if p2 else float('inf')
        graph[virtual_key] = []
        if p1:
            graph[virtual_key].append((best_k1, w1))
            graph.setdefault(best_k1, []).append((virtual_key, w1))
        if p2:
            graph[virtual_key].append((best_k2, w2))
            graph.setdefault(best_k2, []).append((virtual_key, w2))
        return virtual_key, best_point

    def dijkstra_full(self, graph, start_key):
        counter = 0
        queue = [(0, counter, start_key)]
        distances = {start_key: 0}
        previous = {}
        visited = set()
        while queue:
            current_dist, _, current = heapq.heappop(queue)
            if current in visited:
                continue
            visited.add(current)
            for neighbor, weight in graph.get(current, []):
                new_dist = current_dist + weight
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    counter += 1
                    heapq.heappush(queue, (new_dist, counter, neighbor))
        return distances, previous

    def relax_new_vertex(self, graph, distances, previous, key):
        """A virtual snap vertex connects only to its two host edge endpoints
        (k1, k2), which already exist in the cached shortest-path tree. So its
        distance is simply the best of those two, no full recompute needed."""
        best_dist = float('inf')
        best_prev = None
        for neighbor, weight in graph.get(key, []):
            if neighbor in distances:
                candidate = distances[neighbor] + weight
                if candidate < best_dist:
                    best_dist = candidate
                    best_prev = neighbor
        if best_prev is not None:
            distances[key] = best_dist
            previous[key] = best_prev

    def reconstruct_path(self, previous, start_key, end_key):
        if end_key == start_key:
            return [start_key]
        path = [end_key]
        while path[-1] != start_key:
            if path[-1] not in previous:
                return None
            path.append(previous[path[-1]])
        path.reverse()
        return path

    def build_route(self):
        layer = self.selected_layer()
        if not layer or self.start_point is None or self.end_point is None:
            return
        cache = self.get_cached_graph(layer)
        graph = cache['graph']
        point_lookup = cache['point_lookup']
        if not graph:
            QMessageBox.warning(self.iface.mainWindow(), self.tr('route'), self.tr('graph_failed'))
            return

        start_key, start_snap = self.snap_to_graph(self.start_point, cache)
        end_key, end_snap = self.snap_to_graph(self.end_point, cache)
        if start_key is None or end_key is None:
            QMessageBox.warning(self.iface.mainWindow(), self.tr('route'), self.tr('nearest_failed'))
            return

        if cache.get('dijkstra_start_key') == start_key and cache.get('dijkstra_from') is not None:
            distances, previous = cache['dijkstra_from']
        else:
            distances, previous = self.dijkstra_full(graph, start_key)
            cache['dijkstra_start_key'] = start_key
            cache['dijkstra_from'] = (distances, previous)

        if end_key not in distances:
            self.relax_new_vertex(graph, distances, previous, end_key)

        if end_key not in distances:
            QMessageBox.warning(self.iface.mainWindow(), self.tr('route'), self.tr('route_not_found'))
            return

        path_keys = self.reconstruct_path(previous, start_key, end_key)
        if not path_keys:
            QMessageBox.warning(self.iface.mainWindow(), self.tr('route'), self.tr('route_not_found'))
            return
        route_points = [point_lookup[key] for key in path_keys]
        self.update_route_layer(route_points)
        self.iface.messageBar().pushMessage(self.tr('route'), self.tr('route_updated'), level=0, duration=4)

    def get_route_layer(self):
        if self.route_layer_id:
            layer = QgsProject.instance().mapLayer(self.route_layer_id)
            if layer:
                self.route_layer = layer
                return layer
        self.route_layer = None
        self.route_layer_id = None
        return None

    def get_marker_layer(self):
        if self.marker_layer_id:
            layer = QgsProject.instance().mapLayer(self.marker_layer_id)
            if layer:
                return layer
        self.marker_layer_id = None
        return None

    def update_route_style(self):
        route_layer = self.get_route_layer()
        if route_layer and route_layer.isValid():
            symbol = QgsSymbol.defaultSymbol(route_layer.geometryType())
            symbol.setColor(QColor(self.route_color))
            symbol.setWidth(1.2)
            route_layer.renderer().setSymbol(symbol)
            route_layer.triggerRepaint()
            
    def create_start_symbol(self):
        return QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': self.route_color,
            'outline_color': '#ffffff',
            'size': '4.5'
        })

    def create_end_symbol(self):
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': self.route_color,
            'outline_color': '#ffffff',
            'size': '4.5'
        })

        inner = QgsSimpleMarkerSymbolLayer.create({
            'name': 'circle',
            'color': '#ffffff',
            'outline_color': '#ffffff',
            'size': '2'
        })

        symbol.appendSymbolLayer(inner)

        return symbol

    def update_marker_style(self):
        marker_layer = self.get_marker_layer()
        if marker_layer and marker_layer.isValid():
            categories = [
                QgsRendererCategory('start', self.create_start_symbol(), self.tr('start')),
                QgsRendererCategory('end', self.create_end_symbol(), self.tr('end')),
            ]
            marker_layer.setRenderer(QgsCategorizedSymbolRenderer('type', categories))
            marker_layer.triggerRepaint()

    def get_route_group(self):
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(self.tr('shortest_path'))
        if group is None:
            group = root.insertGroup(0, self.tr('shortest_path'))
        return group

    def create_route_layer(self, crs_authid):
        self.route_layer = QgsVectorLayer(f'LineString?crs={crs_authid}', self.tr('route_layer'), 'memory')
        provider = self.route_layer.dataProvider()
        provider.addAttributes([QgsField('name', QVariant.String)])
        self.route_layer.updateFields()
        symbol = QgsSymbol.defaultSymbol(self.route_layer.geometryType())
        symbol.setColor(QColor(self.route_color))
        symbol.setWidth(1.2)
        self.route_layer.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(self.route_layer, False)
        self.get_route_group().addLayer(self.route_layer)
        self.route_layer_id = self.route_layer.id()

    def create_marker_layer(self, crs_authid):
        marker_layer = QgsVectorLayer(f'Point?crs={crs_authid}', self.tr('marker_layer'), 'memory')
        provider = marker_layer.dataProvider()
        provider.addAttributes([QgsField('type', QVariant.String)])
        marker_layer.updateFields()
        categories = [
            QgsRendererCategory('start', self.create_start_symbol(), self.tr('start')),
            QgsRendererCategory('end', self.create_end_symbol(), self.tr('end')),
        ]
        marker_layer.setRenderer(QgsCategorizedSymbolRenderer('type', categories))
        QgsProject.instance().addMapLayer(marker_layer, False)
        self.get_route_group().addLayer(marker_layer)
        self.marker_layer_id = marker_layer.id()
        return marker_layer

    def clear_route_layer(self):
        route_layer = self.get_route_layer()
        if route_layer and route_layer.isValid():
            route_layer.dataProvider().truncate()
            route_layer.updateExtents()
            route_layer.triggerRepaint()

    def clear_marker_layer(self):
        marker_layer = self.get_marker_layer()
        if marker_layer and marker_layer.isValid():
            marker_layer.dataProvider().truncate()
            marker_layer.updateExtents()
            marker_layer.triggerRepaint()

    def update_marker_layer(self, start_point=None, end_point=None):
        layer = self.selected_layer()
        if layer is None:
            return
        marker_layer = self.get_marker_layer()
        if marker_layer is None or not marker_layer.isValid():
            marker_layer = self.create_marker_layer(layer.crs().authid())
        self.clear_marker_layer()
        features = []
        if start_point is not None:
            feat = QgsFeature(marker_layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(start_point))
            feat['type'] = 'start'
            features.append(feat)
        if end_point is not None:
            feat = QgsFeature(marker_layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(end_point))
            feat['type'] = 'end'
            features.append(feat)
        if features:
            marker_layer.dataProvider().addFeatures(features)
        self.update_marker_style()
        marker_layer.updateExtents()
        marker_layer.triggerRepaint()

    def update_route_layer(self, route_points):
        layer = self.selected_layer()
        if layer is None:
            return
        route_layer = self.get_route_layer()
        if route_layer is None or not route_layer.isValid():
            self.create_route_layer(layer.crs().authid())
            route_layer = self.get_route_layer()
        self.clear_route_layer()
        feat = QgsFeature(route_layer.fields())
        feat.setGeometry(QgsGeometry.fromPolylineXY(route_points))
        feat['name'] = self.tr('shortest_path')
        route_layer.dataProvider().addFeature(feat)
        self.update_route_style()
        route_layer.updateExtents()
        route_layer.triggerRepaint()

    @staticmethod
    def point_key(point):
        return (round(point.x(), 6), round(point.y(), 6))

    @staticmethod
    def distance(p1, p2):
        return hypot(p1.x() - p2.x(), p1.y() - p2.y())
