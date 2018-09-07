
class UnitAnimation(QGraphicsItem):
    def __init__(self, unit):
        super().__init__()
        self.animation = SpriteAnimation(unit.name + '.png', unit.size)
        self.motion_timer = QTimer()
        self.animation_timer = QTimer()
        self.unit = unit
        self.init_start_state()
        self.painter = QPainter()
        self.current_frame = 0

    def boundingRect(self):
        return QRectF(self.unit.x * 32, self.unit.y * 32, 32, 32)

    def paint(self, painter, style, widget=None):
        painter.drawPixmap(self.unit.x * 32, self.unit.y * 32, 32, 32, self.animation.get_current_pixmap())

    def init_start_state(self):
        self.motion_timer.timeout.connect(self.move_unit)
        self.animation_timer.timeout.connect(self.animate)
        self.motion_timer.start(170)
        self.animation_timer.start(70)

    def animate(self):
        self.animation.next_frame()
        self.animation.current_direction = self.unit.current_direction
        self.update()

    def move_unit(self):
        self.unit.move()
        #self.setPos(self.unit.x, self.unit.y)
        if not self.unit.stop_moving:
            self.moveBy(32* directions[self.unit.current_direction][0], 32 * directions[self.unit.current_direction][1])
