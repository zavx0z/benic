from app import ma


class PeriodSchema(ma.Schema):
    class Meta:
        fields = ("id", "start_date", "end_date", "direction", "diff_days", "count_videos")


period_schema = PeriodSchema()
periods_schema = PeriodSchema(many=True)
