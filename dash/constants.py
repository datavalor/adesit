# Constants definition
G12_COLUMN_NAME = "_violating_tuple"
G3_COLUMN_NAME = "_g3_to_remove"
SELECTION_COLUMN_NAME = "_selected"
ADESIT_COLUMNS = [G12_COLUMN_NAME, G3_COLUMN_NAME, SELECTION_COLUMN_NAME]

ADESIT_INDEX = "id"

TSNE_AXES = ['__t-SNE1', '__t-SNE2']
PCA_AXES = ['__PCA1', '__PCA2']
VIZ_PROJ = PCA_AXES+TSNE_AXES

TABLE_MAX_ROWS = 16

SELECTED_COLOR_BAD = "#EFF22C"
SELECTED_COLOR_GOOD = "#008000"
CE_COLOR = "#EF553B"