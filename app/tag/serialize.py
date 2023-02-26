from app import ma


class TagSchema(ma.Schema):
    class Meta:
        fields = ("id", "name",)


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
