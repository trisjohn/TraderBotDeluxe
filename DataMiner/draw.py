

class ClickToDrawPoints(object):
    def __init__(self, ax):
        self.ax = ax
        self.fig = ax.figure
        self.xy = []
        self.points = ax.scatter([], [], s=200, color='red', picker=20)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes is None:
            return
        self.xy.append([event.xdata, event.ydata])
        self.points.set_offsets(self.xy)
        self.ax.draw_artist(self.points)
        self.fig.canvas.blit(self.ax.bbox)

    def show(self):
        plt.show()