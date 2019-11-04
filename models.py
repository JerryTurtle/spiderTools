from exts import db


class PolicySpiderUrlInfo(db.Model):
    __tablename__ = 'policy_spider_url_info'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = db.Column(db.Integer)
    type1 = db.Column(db.String(64))
    type2 = db.Column(db.String(64))
    type3 = db.Column(db.String(64))
    type4 = db.Column(db.String(64))
    type5 = db.Column(db.String(64))
    url = db.Column(db.Text)
    insert_time = db.Column(db.DateTime)
    from_url = db.Column(db.String(255))

    # def __init__(self, task_id, type1, type2, type3, type4, type5):
    #     self.task_id = task_id
    #     self.type1 = type1
    #     self.type2 = type2
    #     self.type3 = type3
    #     self.type4 = type4
    #     self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderUrlInfo %r>' % self.task_id


class PolicySpiderTaskInfo(db.Model):
    __tablename__ = 'policy_spider_task_info'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = db.Column(db.Integer)
    home_url = db.Column(db.String(300))
    start_url = db.Column(db.String(255))
    spider_type = db.Column(db.Integer)
    state = db.Column(db.Integer)
    type1 = db.Column(db.String(64))
    type2 = db.Column(db.String(64))
    type3 = db.Column(db.String(64))
    type4 = db.Column(db.String(64))
    type5 = db.Column(db.String(64))

    rules_organization = db.Column(db.String(512))
    rules_subject = db.Column(db.String(512))
    rules_keywords = db.Column(db.String(512))
    rules_file_number = db.Column(db.String(512))
    rules_create_date = db.Column(db.String(512))
    rules_release_date = db.Column(db.String(512))
    rules_enforcement_date = db.Column(db.String(512))
    rules_invalid_date = db.Column(db.String(512))
    rules_index_number = db.Column(db.String(512))
    rules_author = db.Column(db.String(512))

    urls = db.Column(db.Text)
    url_head = db.Column(db.String(255))
    rules_url = db.Column(db.String(512))
    rules_next_page = db.Column(db.String(512))
    ajax_url = db.Column(db.Text)
    ajax_data = db.Column(db.Text)
    insert_time = db.Column(db.DateTime)
    extension_1 = db.Column(db.String(512))

    # def __init__(self, task_id, type1, type2, type3, type4, type5):
    #     self.task_id = task_id
    #     self.type1 = type1
    #     self.type2 = type2
    #     self.type3 = type3
    #     self.type4 = type4
    #     self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderTaskInfo %r>' % self.task_id


class PolicyDataAnalysisRules(db.Model):
    __tablename__ = 'policy_data_analysis_rules'

    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = db.Column(db.Integer)

    meaning = db.Column(db.String(512))
    rule_name = db.Column(db.String(512))
    rule_type = db.Column(db.String(512))
    rule = db.Column(db.String(512))

    insert_time = db.Column(db.DateTime)

    # def __init__(self, task_id,):
    #     self.task_id = task_id

    def __repr__(self):
        return '<PolicyDataAnalysisRules %r>' % self.id_


class PolicySpiderDataInfo(db.Model):
    __tablename__ = 'policy_spider_data_info'
    id_ = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = db.Column(db.Integer)
    type1 = db.Column(db.String(64))
    type2 = db.Column(db.String(64))
    type3 = db.Column(db.String(64))
    type4 = db.Column(db.String(64))
    type5 = db.Column(db.String(64))

    title = db.Column(db.String(1024))
    content = db.Column(db.Text)
    author = db.Column(db.String(1024))
    organization = db.Column(db.String(1024))
    subject = db.Column(db.String(1024))
    keywords = db.Column(db.String(1024))
    file_number = db.Column(db.String(1024))
    create_date = db.Column(db.String(1024))
    release_date = db.Column(db.String(1024))
    enforcement_date = db.Column(db.String(1024))
    invalid_date = db.Column(db.String(1024))
    index_number = db.Column(db.String(1024))

    image_path = db.Column(db.String(1024))
    attachment = db.Column(db.String(1024))

    url = db.Column(db.Text)
    insert_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<PolicySpiderDataInfo %r>' % self.task_id
