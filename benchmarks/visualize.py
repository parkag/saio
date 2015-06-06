import numpy as np


benchmark = np.loadtxt('query.saio.out')

pots = k.estimated_pots
mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(benchmark),
				plane_orientation='x_axes',
				slice_index=10,
				)
mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(benchmark),
				plane_orientation='y_axes',
				slice_index=10,
				)
mlab.outline()