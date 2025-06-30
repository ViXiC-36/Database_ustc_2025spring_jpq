-- Active: 1744278957744@@127.0.0.1@3306@academia
-- 1. 教师表
DROP TABLE IF EXISTS Teacher;
CREATE TABLE Teacher (
    teacher_id  VARCHAR(5) PRIMARY KEY COMMENT '工号',
    name        VARCHAR(256) NOT NULL COMMENT '姓名',
    gender      TINYINT NOT NULL COMMENT '性别',    -- 1-男，2-女
    title       TINYINT NOT NULL COMMENT '职称'    
    -- 1-博士后，2-助教，3-讲师，4-副教授，5-特任教授，6-教授，7-助理研究员，8-特任副研究员，9-副研究员，10-特任研究员，11-研究员
);

-- 2. 课程表
DROP TABLE IF EXISTS Course;
CREATE TABLE Course (
    course_id   VARCHAR(256) PRIMARY KEY COMMENT '课程号',
    course_name VARCHAR(256) NOT NULL COMMENT '课程名称',
    total_hours INT NOT NULL COMMENT '学时数',
    property    TINYINT NOT NULL COMMENT '课程性质'    -- 1-本科，2-研究生
);

-- 3. 论文表
DROP TABLE IF EXISTS Paper;
CREATE TABLE Paper (
    paper_id           INT PRIMARY KEY COMMENT '序号',
    paper_name         VARCHAR(256) NOT NULL COMMENT '论文名称',
    pub_source         VARCHAR(256) NOT NULL COMMENT '发表源',
    pub_year           YEAR NOT NULL COMMENT '发表年份',
    paper_type         TINYINT NOT NULL COMMENT '类型',  -- 1-full paper，2-short paper，3-poster paper，4-demo paper
    paper_level        TINYINT NOT NULL COMMENT '级别'   -- 1-CCF-A，2-CCF-B，3-CCF-C，4-中文CCF-A，5-中文CCFB，6-无级别
);

-- 4. 项目表
DROP TABLE IF EXISTS Project;
CREATE TABLE Project (
    project_id    VARCHAR(256) PRIMARY KEY COMMENT '项目号',
    project_name  VARCHAR(256) NOT NULL COMMENT '项目名称',
    project_source VARCHAR(256) NOT NULL COMMENT '项目来源',
    project_type  TINYINT      NOT NULL COMMENT '项目类型',  -- 1-国家级项目，2-省部级项目，3-市厅级项目，4-企业合作项目，5-其它类型项目
    total_fund    DECIMAL(12,2) NOT NULL COMMENT '总经费',
    start_year    INT NOT NULL COMMENT '开始年份',  
    end_year      INT NOT NULL COMMENT '结束年份'   
);

-- 5. 教师上课表
DROP TABLE IF EXISTS Teacher_Course;
CREATE TABLE Teacher_Course (
    id_teaching  INT AUTO_INCREMENT PRIMARY KEY COMMENT '序号',

    teacher_id  VARCHAR(5) NOT NULL COMMENT '工号',
    course_id   VARCHAR(256) NOT NULL COMMENT '课程号',

    year    INT NOT NULL COMMENT '年份',
    semester INT NOT NULL COMMENT '学期',  -- 1-春季学期，2-夏季学期，3-秋季学期
    my_hours INT NOT NULL COMMENT '承担学时',
    FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Course(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (teacher_id, course_id, year, semester)
);

-- 6. 教师论文表
DROP TABLE IF EXISTS Teacher_Paper;
CREATE TABLE Teacher_Paper (
    id_publish  INT AUTO_INCREMENT PRIMARY KEY COMMENT '序号',

    teacher_id  VARCHAR(5) NOT NULL COMMENT '工号',
    paper_id           INT NOT NULL COMMENT '序号',

    author_rank        INT NOT NULL COMMENT '排名',
    is_corresponding BOOLEAN NOT NULL COMMENT '是否通讯作者',
    FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES Paper(paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (teacher_id, paper_id, author_rank, is_corresponding)
)

-- 7. 教师项目表
DROP TABLE IF EXISTS Teacher_Project;
CREATE TABLE Teacher_Project (
    id_principal INT AUTO_INCREMENT PRIMARY KEY COMMENT '序号',

    teacher_id  VARCHAR(5) NOT NULL COMMENT '工号',
    project_id  VARCHAR(256) NOT NULL COMMENT '项目号',

    principal_rank INT NOT NULL COMMENT '排名',
    my_fund DECIMAL(12,2) NOT NULL COMMENT '承担经费',
    FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (project_id) REFERENCES Project(project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (teacher_id, project_id, principal_rank, my_fund)
);