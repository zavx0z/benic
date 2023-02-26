from app import ma
from app.tag.serialize import TagSchema


class VideoSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "tags")

    tags = ma.Nested(TagSchema, many=True)


video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)
