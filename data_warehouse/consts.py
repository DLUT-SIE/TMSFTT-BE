'''define enum data'''


class EnumData:
    ''' define enum data'''
    TEACHERS_STATISTICS = 0
    RECORDS_STATISTICS = 1
    COVERAGE_STATISTICS = 2
    TRAINING_HOURS_WORKLOAD_STATISTICS = 3

    BY_DEPARTMENT = 0
    BY_TECHNICAL_TITLE = 1
    BY_AGE_DISTRIBUTION = 2
    BY_HIGHEST_DEGREE = 3
    BY_TOTAL_TEACHERS_NUM = 0
    BY_TOTAL_TRAINING_HOURS = 1
    BY_AVERAGE_TRAINING_HOURS = 2
    BY_TOTAL_WORKLOAD = 3
    BY_AVERAGE_WORKLOAD = 4

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
    TRAINING_HOURS_GROUPING_CHOICES = (
        (BY_TOTAL_TEACHERS_NUM, '按总人数', 'BY_TOTAL_TEACHERS_NUM'),
        (BY_TOTAL_TRAINING_HOURS, '按总培训学时', 'BY_TOTAL_TRAINING_HOURS'),
        (BY_AVERAGE_TRAINING_HOURS, '按人均培训学时', 'BY_AVERAGE_\
            TRAINING_HOURS'),
        (BY_TOTAL_WORKLOAD, '按总工作量', 'BY_TOTAL_WORKLOAD'),
        (BY_AVERAGE_WORKLOAD, '按人均工作量', 'BY_AVERAGE_WORKLOAD')
    )

    TITLE_LABEL = ('教授', '副教授', '讲师（高校）', '助教（高校）', '研究员', '副研究员',
                   '助理研究员', '工程师', '高级工程师', '教授级高工', '其他')
    EDUCATION_BACKGROUD_LABEL = ('博士研究生毕业', '研究生毕业', '大学本科毕业')
    AGE_LABEL = ('35岁及以下', '36-45岁', '46-55岁', '56岁及以上')
