class ParagraphStyle:
    def __init__(self, name, parent=None, **kwargs):
        self.name = name
        self.parent = parent
        self.__dict__.update(kwargs)

def getSampleStyleSheet():
    return {
        'Title': ParagraphStyle('Title'),
        'Heading1': ParagraphStyle('Heading1'),
        'Heading2': ParagraphStyle('Heading2'),
        'BodyText': ParagraphStyle('BodyText'),
    }
