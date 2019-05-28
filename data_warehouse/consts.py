'''define enum data'''


class EnumData:
    ''' define enum data'''
    TEACHERS_STATISTICS = 0
    RECORDS_STATISTICS = 1
    COVERAGE_STATISTICS = 2
    TRAINING_HOURS_STATISTICS = 3

    BY_DEPARTMENT = 0
    BY_TECHNICAL_TITLE = 1
    BY_AGE_DISTRIBUTION = 2
    BY_HIGHEST_DEGREE = 3

    GROUP_BY_LIST = (
        BY_DEPARTMENT,
        BY_TECHNICAL_TITLE,
        BY_AGE_DISTRIBUTION,
        BY_HIGHEST_DEGREE
    )

    TEACHERS_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_TECHNICAL_TITLE, '按职称', 'BY_TECHNICAL_TITLE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION'),
        (BY_HIGHEST_DEGREE, '按最高学位', 'BY_HIGHEST_DEGREE')
    )
    TRAINEE_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_TECHNICAL_TITLE, '按职称', 'BY_TECHNICAL_TITLE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION')
    )

    TITLE_LABEL = ('教授', '副教授', '讲师（高校）', '助教（高校）', '研究员', '副研究员',
                   '助理研究员', '工程师', '高级工程师', '教授级高工', '其他')
    EDUCATION_BACKGROUD_LABEL = ('博士研究生毕业', '研究生毕业', '大学本科毕业')
    AGE_LABEL = ('35岁及以下', '36-45岁', '46-55岁', '56岁及以上')
