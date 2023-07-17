from mongoengine import EmbeddedDocument, Document, connect
from mongoengine.fields import DateField, EmbeddedDocumentField, ListField, StringField, ReferenceField

connect(host='mongodb+srv://lokfaaddiiv:admin@lokfaaddiiv.pdegaqw.mongodb.net/HW9?retryWrites=true&w=majority')

# -----------------------------------------------------------------


class Author(Document):
    fullname = StringField()
    born_date = DateField()
    born_location = StringField()
    description = StringField()


class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author)
    quote = StringField()


# -----------------------------------------------------------------
