class PtahBullet(Bullet):
    def __init__(self, id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.choices = choices
        self.id = id

    @keyhandler.register(NEWLINE_KEY)
    def accept(self):
        super().accept()

    #def launch(self):
    #    result = super().launch()
    #    return result
