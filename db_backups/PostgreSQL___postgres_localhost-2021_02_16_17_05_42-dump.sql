--
-- PostgreSQL database dump
--

-- Dumped from database version 12.5 (Ubuntu 12.5-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.5 (Ubuntu 12.5-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: concurent_site; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA concurent_site;


ALTER SCHEMA concurent_site OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE concurent_site.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_group_id_seq OWNED BY concurent_site.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE concurent_site.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_group_permissions_id_seq OWNED BY concurent_site.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE concurent_site.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_permission_id_seq OWNED BY concurent_site.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE concurent_site.auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE concurent_site.auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_user_groups_id_seq OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_user_groups_id_seq OWNED BY concurent_site.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_user_id_seq OWNER TO postgres;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_user_id_seq OWNED BY concurent_site.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE concurent_site.auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.auth_user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.auth_user_user_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.auth_user_user_permissions_id_seq OWNED BY concurent_site.auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE concurent_site.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.django_admin_log_id_seq OWNED BY concurent_site.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE concurent_site.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.django_content_type_id_seq OWNED BY concurent_site.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE concurent_site.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.django_migrations_id_seq OWNED BY concurent_site.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE concurent_site.django_session OWNER TO postgres;

--
-- Name: main_domain; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_domain (
    name character varying(100) NOT NULL,
    age integer NOT NULL,
    unique_backlinks integer NOT NULL,
    total_backlinks integer NOT NULL,
    status character varying(10) NOT NULL
);


ALTER TABLE concurent_site.main_domain OWNER TO postgres;

--
-- Name: main_handledxml; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_handledxml (
    request character varying(100) NOT NULL,
    xml text NOT NULL,
    status character varying(10) NOT NULL
);


ALTER TABLE concurent_site.main_handledxml OWNER TO postgres;

--
-- Name: main_order; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_order (
    id integer NOT NULL,
    request_id integer NOT NULL,
    user_id integer NOT NULL,
    order_id integer NOT NULL
);


ALTER TABLE concurent_site.main_order OWNER TO postgres;

--
-- Name: main_order_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_order_id_seq OWNER TO postgres;

--
-- Name: main_order_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_order_id_seq OWNED BY concurent_site.main_order.id;


--
-- Name: main_orderstatus; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_orderstatus (
    order_id integer NOT NULL,
    status smallint NOT NULL,
    progress smallint NOT NULL,
    user_id integer NOT NULL,
    ordered_keywords_amount smallint NOT NULL,
    user_order_id integer NOT NULL
);


ALTER TABLE concurent_site.main_orderstatus OWNER TO postgres;

--
-- Name: main_orderstatus_order_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_orderstatus_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_orderstatus_order_id_seq OWNER TO postgres;

--
-- Name: main_orderstatus_order_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_orderstatus_order_id_seq OWNED BY concurent_site.main_orderstatus.order_id;


--
-- Name: main_payload; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_payload (
    key character varying(100) NOT NULL,
    balance integer NOT NULL
);


ALTER TABLE concurent_site.main_payload OWNER TO postgres;

--
-- Name: main_request; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_request (
    request_id integer NOT NULL,
    request_text character varying(100) NOT NULL,
    site_age_concurency integer NOT NULL,
    site_stem_concurency integer NOT NULL,
    site_volume_concurency integer NOT NULL,
    site_backlinks_concurency integer NOT NULL,
    site_total_concurency double precision NOT NULL,
    direct_upscale double precision NOT NULL,
    status character varying(100) NOT NULL,
    site_direct_concurency integer NOT NULL,
    site_seo_concurency integer NOT NULL
);


ALTER TABLE concurent_site.main_request OWNER TO postgres;

--
-- Name: main_request_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_request_id_seq OWNER TO postgres;

--
-- Name: main_request_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_request_id_seq OWNED BY concurent_site.main_request.request_id;


--
-- Name: main_request_request_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_request_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_request_request_id_seq OWNER TO postgres;

--
-- Name: main_request_request_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_request_request_id_seq OWNED BY concurent_site.main_request.request_id;


--
-- Name: main_requestqueue; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_requestqueue (
    request_text character varying(100) NOT NULL
);


ALTER TABLE concurent_site.main_requestqueue OWNER TO postgres;

--
-- Name: main_ticket; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_ticket (
    ticket_id integer NOT NULL,
    author_id integer NOT NULL,
    status character varying(15) NOT NULL,
    opened timestamp with time zone NOT NULL,
    closed timestamp with time zone,
    user_ticket_id integer NOT NULL
);


ALTER TABLE concurent_site.main_ticket OWNER TO postgres;

--
-- Name: main_ticket_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_ticket_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_ticket_id_seq OWNER TO postgres;

--
-- Name: main_ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_ticket_id_seq OWNED BY concurent_site.main_ticket.ticket_id;


--
-- Name: main_ticket_ticket_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_ticket_ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_ticket_ticket_id_seq OWNER TO postgres;

--
-- Name: main_ticket_ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_ticket_ticket_id_seq OWNED BY concurent_site.main_ticket.ticket_id;


--
-- Name: main_ticketpost; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_ticketpost (
    ticket_post_id integer NOT NULL,
    ticket_id integer NOT NULL,
    ticket_post_author_id integer NOT NULL,
    ticket_post_text text NOT NULL,
    ticket_post_order smallint NOT NULL
);


ALTER TABLE concurent_site.main_ticketpost OWNER TO postgres;

--
-- Name: main_ticketpost_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_ticketpost_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_ticketpost_id_seq OWNER TO postgres;

--
-- Name: main_ticketpost_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_ticketpost_id_seq OWNED BY concurent_site.main_ticketpost.ticket_post_id;


--
-- Name: main_ticketpost_ticket_post_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_ticketpost_ticket_post_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_ticketpost_ticket_post_id_seq OWNER TO postgres;

--
-- Name: main_ticketpost_ticket_post_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_ticketpost_ticket_post_id_seq OWNED BY concurent_site.main_ticketpost.ticket_post_id;


--
-- Name: main_userdata; Type: TABLE; Schema: concurent_site; Owner: postgres
--

CREATE TABLE concurent_site.main_userdata (
    user_id integer NOT NULL,
    balance integer NOT NULL,
    ordered_keywords integer NOT NULL,
    orders_amount integer NOT NULL
);


ALTER TABLE concurent_site.main_userdata OWNER TO postgres;

--
-- Name: main_userdata_id_seq; Type: SEQUENCE; Schema: concurent_site; Owner: postgres
--

CREATE SEQUENCE concurent_site.main_userdata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concurent_site.main_userdata_id_seq OWNER TO postgres;

--
-- Name: main_userdata_id_seq; Type: SEQUENCE OWNED BY; Schema: concurent_site; Owner: postgres
--

ALTER SEQUENCE concurent_site.main_userdata_id_seq OWNED BY concurent_site.main_userdata.user_id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_permission ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('concurent_site.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_admin_log ALTER COLUMN id SET DEFAULT nextval('concurent_site.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_content_type ALTER COLUMN id SET DEFAULT nextval('concurent_site.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_migrations ALTER COLUMN id SET DEFAULT nextval('concurent_site.django_migrations_id_seq'::regclass);


--
-- Name: main_order id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_order ALTER COLUMN id SET DEFAULT nextval('concurent_site.main_order_id_seq'::regclass);


--
-- Name: main_orderstatus order_id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_orderstatus ALTER COLUMN order_id SET DEFAULT nextval('concurent_site.main_orderstatus_order_id_seq'::regclass);


--
-- Name: main_request request_id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_request ALTER COLUMN request_id SET DEFAULT nextval('concurent_site.main_request_request_id_seq'::regclass);


--
-- Name: main_ticket ticket_id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticket ALTER COLUMN ticket_id SET DEFAULT nextval('concurent_site.main_ticket_ticket_id_seq'::regclass);


--
-- Name: main_ticketpost ticket_post_id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticketpost ALTER COLUMN ticket_post_id SET DEFAULT nextval('concurent_site.main_ticketpost_ticket_post_id_seq'::regclass);


--
-- Name: main_userdata user_id; Type: DEFAULT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_userdata ALTER COLUMN user_id SET DEFAULT nextval('concurent_site.main_userdata_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add domain	1	add_domain
2	Can change domain	1	change_domain
3	Can delete domain	1	delete_domain
4	Can view domain	1	view_domain
5	Can add handled xml	2	add_handledxml
6	Can change handled xml	2	change_handledxml
7	Can delete handled xml	2	delete_handledxml
8	Can view handled xml	2	view_handledxml
9	Can add payload	3	add_payload
10	Can change payload	3	change_payload
11	Can delete payload	3	delete_payload
12	Can view payload	3	view_payload
13	Can add request	4	add_request
14	Can change request	4	change_request
15	Can delete request	4	delete_request
16	Can view request	4	view_request
17	Can add request queue	5	add_requestqueue
18	Can change request queue	5	change_requestqueue
19	Can delete request queue	5	delete_requestqueue
20	Can view request queue	5	view_requestqueue
21	Can add user statement	6	add_userstatement
22	Can change user statement	6	change_userstatement
23	Can delete user statement	6	delete_userstatement
24	Can view user statement	6	view_userstatement
25	Can add log entry	7	add_logentry
26	Can change log entry	7	change_logentry
27	Can delete log entry	7	delete_logentry
28	Can view log entry	7	view_logentry
29	Can add permission	8	add_permission
30	Can change permission	8	change_permission
31	Can delete permission	8	delete_permission
32	Can view permission	8	view_permission
33	Can add group	9	add_group
34	Can change group	9	change_group
35	Can delete group	9	delete_group
36	Can view group	9	view_group
37	Can add user	10	add_user
38	Can change user	10	change_user
39	Can delete user	10	delete_user
40	Can view user	10	view_user
41	Can add content type	11	add_contenttype
42	Can change content type	11	change_contenttype
43	Can delete content type	11	delete_contenttype
44	Can view content type	11	view_contenttype
45	Can add session	12	add_session
46	Can change session	12	change_session
47	Can delete session	12	delete_session
48	Can view session	12	view_session
49	Can add order	13	add_order
50	Can change order	13	change_order
51	Can delete order	13	delete_order
52	Can view order	13	view_order
53	Can add user data	14	add_userdata
54	Can change user data	14	change_userdata
55	Can delete user data	14	delete_userdata
56	Can view user data	14	view_userdata
57	Can add order status	15	add_orderstatus
58	Can change order status	15	change_orderstatus
59	Can delete order status	15	delete_orderstatus
60	Can view order status	15	view_orderstatus
61	Can add ticket post	16	add_ticketpost
62	Can change ticket post	16	change_ticketpost
63	Can delete ticket post	16	delete_ticketpost
64	Can view ticket post	16	view_ticketpost
65	Can add ticket	17	add_ticket
66	Can change ticket	17	change_ticket
67	Can delete ticket	17	delete_ticket
68	Can view ticket	17	view_ticket
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
16	pbkdf2_sha256$216000$tj2BMJEPZcaE$izSggF32GY80GWVLcSrjORpHYFF5kZ756hpYegt0iLg=	2021-02-10 14:38:14.88318+03	f	sup			aaa@aaa.com	f	t	2021-02-10 14:38:14.404912+03
28	pbkdf2_sha256$216000$GEEI2YAbxoka$XOX3fKdMtinhGrthM0YHJv+oEx+uxlrUJN71SOJiiAY=	2021-02-15 15:28:18.882968+03	f	new6			newbie6@ya.com	f	t	2021-02-15 15:09:14.760696+03
18	pbkdf2_sha256$216000$HYSnbB8kIh3o$zP9d85pZ7CwcdXnOWJu8hIlGYO1k1/nZftai9N39G70=	2021-02-10 15:39:34.814925+03	f	final			final@aaa.ru	f	t	2021-02-10 15:39:34.34355+03
19	pbkdf2_sha256$216000$8DEWqR7Fdrcb$XwL7sUnB7mSuxuMcMmc7vjCjCs+d8LRi8zQI2uztnxk=	2021-02-11 12:36:21.403979+03	f	Wenfort			frenther2016@ya.ru	f	t	2021-02-11 12:36:20.856512+03
23	pbkdf2_sha256$216000$YhngINsKHZYc$fFNgE5nqMo7k8xKCwnZyj1wN6cYDF5nULccfl0ZIQNM=	2021-02-15 18:52:08.129439+03	f	new			newbie@ya.com	f	t	2021-02-13 15:13:00.408524+03
29	pbkdf2_sha256$216000$KgfkTODqMq9c$7GTCWFNbGQSb7ZpcR62YWlIu6+GVlyeZVczYs/bHoR4=	2021-02-15 19:09:28.599409+03	f	lll			aaajk@ya.ru	f	t	2021-02-15 19:09:27.940822+03
30	pbkdf2_sha256$216000$HxMesZfxlx9s$PrQemYg69vubYSXJwonfFzngsfyyNXH+ObSH6cVDkGI=	2021-02-15 19:11:01.259542+03	f	tester@losik.ru			losik_tester@losik.ru	f	t	2021-02-15 19:11:00.817252+03
22	pbkdf2_sha256$216000$d8Yr6ml5popU$3KX7iifqx6feL4dVEIq7pRwBG4o11YSZzYsAVnhmjUw=	2021-02-12 11:47:38.679073+03	f	qq			yjytjyt@213.hh	f	t	2021-02-12 11:47:38.241032+03
21	pbkdf2_sha256$216000$jaFIQmwcymRy$sO7VZA2+rmzVg9XxQkhALmbmQMRRWE+6pP8gF0k25Jg=	2021-02-12 12:13:08.775577+03	f	tu			xcxz@a.ru	f	t	2021-02-12 11:39:13.603468+03
24	pbkdf2_sha256$216000$VnOqBSgZG5Yx$obop9JT7KkInegXYtzas3A6WJ7C5P+mznQnXIYPFN44=	2021-02-13 15:32:22.210379+03	f	new2			newbie2@ya.com	f	t	2021-02-13 15:32:21.776238+03
25	pbkdf2_sha256$216000$cIX0dtPSPtT0$y5IAVIkncwMgLAQ34gWm078DdEQkXOjxd17NM3EUhRc=	2021-02-13 15:57:59.081878+03	f	new3			newbie3@ya.com	f	t	2021-02-13 15:57:58.641135+03
26	pbkdf2_sha256$216000$nn2dHWSwzyP5$5Y++F2QuH2V2TIRg4Q/aRp6IFEYLKgyNM7AJwUgSGC0=	2021-02-13 16:29:09.737178+03	f	new4			newbie4@ya.com	f	t	2021-02-13 16:29:09.256832+03
27	pbkdf2_sha256$216000$sP9kFijznZxD$i4hAvK3cUxs7YUbIfu+5hzQP6tYI5IBOEs46+66d/VA=	2021-02-15 19:35:29.137128+03	f	new5			newbie5@ya.com	f	t	2021-02-13 17:03:30.803329+03
17	pbkdf2_sha256$216000$dkTHAOvAg7M0$HvO8poq5p4tOzgFzSLwc+5IFrDW/WdP9nDoEHw62KDI=	2021-02-16 13:30:03.06675+03	t	airlove			misteriska@ya.ru	t	t	2021-02-10 14:51:22.516729+03
31	pbkdf2_sha256$216000$GwdvLmIZi9G4$0emjY19xOHDiCGpKAfMd8lauDLyYeLwL1rsOIr6ZTOw=	2021-02-16 13:30:26.494126+03	f	new7			newbie7@ya.com	f	t	2021-02-16 13:28:49.168722+03
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.django_content_type (id, app_label, model) FROM stdin;
1	main	domain
2	main	handledxml
3	main	payload
4	main	request
5	main	requestqueue
6	main	userstatement
7	admin	logentry
8	auth	permission
9	auth	group
10	auth	user
11	contenttypes	contenttype
12	sessions	session
13	main	order
14	main	userdata
15	main	orderstatus
16	main	ticketpost
17	main	ticket
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2021-01-19 23:21:19.11938+03
2	auth	0001_initial	2021-01-19 23:21:19.187532+03
3	admin	0001_initial	2021-01-19 23:21:19.271515+03
4	admin	0002_logentry_remove_auto_add	2021-01-19 23:21:19.2945+03
5	admin	0003_logentry_add_action_flag_choices	2021-01-19 23:21:19.303497+03
6	contenttypes	0002_remove_content_type_name	2021-01-19 23:21:19.322484+03
7	auth	0002_alter_permission_name_max_length	2021-01-19 23:21:19.332477+03
8	auth	0003_alter_user_email_max_length	2021-01-19 23:21:19.342483+03
9	auth	0004_alter_user_username_opts	2021-01-19 23:21:19.351465+03
10	auth	0005_alter_user_last_login_null	2021-01-19 23:21:19.359461+03
11	auth	0006_require_contenttypes_0002	2021-01-19 23:21:19.361459+03
12	auth	0007_alter_validators_add_error_messages	2021-01-19 23:21:19.370455+03
13	auth	0008_alter_user_username_max_length	2021-01-19 23:21:19.388443+03
14	auth	0009_alter_user_last_name_max_length	2021-01-19 23:21:19.397438+03
15	auth	0010_alter_group_name_max_length	2021-01-19 23:21:19.408467+03
16	auth	0011_update_proxy_permissions	2021-01-19 23:21:19.416463+03
17	auth	0012_alter_user_first_name_max_length	2021-01-19 23:21:19.426549+03
18	main	0001_initial	2021-01-19 23:21:19.47352+03
19	sessions	0001_initial	2021-01-19 23:21:19.505502+03
20	main	0002_auto_20210202_0806	2021-02-03 07:13:48.027732+03
21	main	0003_auto_20210202_0835	2021-02-03 07:13:48.078985+03
22	main	0004_order_userdata	2021-02-03 07:13:48.247316+03
23	main	0005_auto_20210202_1549	2021-02-03 07:13:48.292171+03
24	main	0006_order_order_id	2021-02-03 07:13:48.312967+03
25	main	0007_auto_20210202_1618	2021-02-03 07:13:48.351779+03
26	main	0008_order_status	2021-02-04 14:43:54.883423+03
27	main	0009_auto_20210204_1148	2021-02-04 14:49:29.811782+03
28	main	0010_auto_20210205_0528	2021-02-05 08:28:39.401846+03
29	main	0011_orderstatus_progress	2021-02-05 10:18:42.192116+03
30	main	0012_orderstatus_user_id	2021-02-05 10:44:29.076513+03
31	main	0013_orderstatus_ordered_keywords_amount	2021-02-05 12:51:04.09759+03
32	main	0014_auto_20210205_1301	2021-02-05 16:01:51.564076+03
33	main	0015_ticketpost	2021-02-06 12:19:00.064693+03
34	main	0016_auto_20210206_1159	2021-02-06 14:59:20.609849+03
35	main	0017_auto_20210206_1312	2021-02-06 16:12:59.484562+03
36	main	0018_auto_20210207_0835	2021-02-07 11:35:38.248632+03
37	main	0019_auto_20210208_0534	2021-02-08 08:34:30.311862+03
38	main	0020_auto_20210210_0612	2021-02-10 09:13:28.262207+03
39	main	0021_auto_20210210_0615	2021-02-10 09:16:11.737121+03
40	main	0022_auto_20210210_0633	2021-02-10 09:33:52.625601+03
41	main	0023_auto_20210210_0644	2021-02-10 09:45:53.787162+03
42	main	0024_auto_20210210_0649	2021-02-10 09:49:03.529904+03
43	main	0025_auto_20210210_0659	2021-02-10 09:59:15.384363+03
44	main	0026_auto_20210210_0744	2021-02-10 10:45:01.954307+03
45	main	0027_auto_20210210_1029	2021-02-10 13:29:27.463467+03
46	main	0028_auto_20210210_1131	2021-02-10 14:33:43.455506+03
47	main	0029_auto_20210210_1143	2021-02-10 14:43:28.756775+03
48	main	0030_auto_20210211_0820	2021-02-11 11:20:24.926421+03
49	main	0031_orderstatus_user_order_id	2021-02-13 14:32:59.440989+03
50	main	0032_ticket_user_ticket_id	2021-02-13 15:22:27.319027+03
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.django_session (session_key, session_data, expire_date) FROM stdin;
zlvlk8q1nk186kvw7mgbttqkgaodtje1	e30:1l8JNt:nBriI68IC2SQwS_EMSNfVzy7zVKGky2_1Dk4dPl4Pjc	2021-02-20 11:56:05.178847+03
5oc03upcd5o9wujbajuch3obm01mxtsy	e30:1l8z19:wrFu72uPb7mw6gK-ohLUzbtzIjjUBJQhiV93V81EPc8	2021-02-22 08:23:23.489945+03
hll1rl6h2uzu3xs6gg4737ickzkdfawy	e30:1l8z1Z:le0vU0_dZn8MFjARGjcSu6ejQ4I42LHIkUrmfFMHVWo	2021-02-22 08:23:49.800789+03
qod1gxamf3gop98hmtn7vri204kur2yp	e30:1l8z1j:pHsUi0XfOl2FbJAAKUXFIOOB99J0vOetFXMDx9E6D4g	2021-02-22 08:23:59.807397+03
tlji4d2ls9hkk001jildx0grlrf612ic	.eJxVjMEOwiAQRP-FsyEU2AIevfsNZGG3tmogKe3J-O9K0oMmc5r3Zl4i4r7NcW-8xoXEWQzi9NslzA8uHdAdy63KXMu2Lkl2RR60yWslfl4O9-9gxjb3NSoaFCRmm0cdEoFGlQAdeKPQhSkrBoMW3AQcrB5GIvONZwfsvBbvD_J-OAA:1l8zHY:xTL3IVukO9fIbNTznbGBsX9ChREtxOW3LPsz6kIzZf4	2021-02-22 08:40:20.293151+03
vnew38fsuce3h6lbplyu0hvz9kermtvl	e30:1l94SJ:144oCu6hb-exAuqQ6omsKaTKpW-nDB00dZy_fBLEEzs	2021-02-22 14:11:47.119258+03
pu9kn13ljnqp9jafkp4xihpkg40t5lwo	e30:1l94f5:43QVgBsRzUTcJYfpi9SCsED4kwu27AZM_yKfMvuQLOw	2021-02-22 14:24:59.734412+03
78nplxsjz5jfc5n07grdyvlcxygxzqx9	e30:1l94fI:Z-EmFmdOn9SZ0kAODcaJhpKK4IHNGfyGtfoGoRyxgyQ	2021-02-22 14:25:12.66478+03
1pxqhly7bmalhp2k2q5x013vcwzaxtd8	e30:1l96BK:ed26x-OtJgOfj0u1ETFRChOA5WK46g1SrCV0eApexKg	2021-02-22 16:02:22.791854+03
hix8xcbqoromo69qdi42o6z3fmelvbgw	e30:1l96BT:ZOdMOxqnrjxGANI8RDYVYI6ezzR9nwoAAuXFsbccQ7A	2021-02-22 16:02:31.065259+03
8r89knwz8cghj2ez80ze3vvm95adewwb	.eJxVjMsOwiAUBf-FtSE8pIBL9_0Gch8gVUOT0q6M_65NutDtmZnzEgm2taat5yVNLC7CanH6HRHokdtO-A7tNkua27pMKHdFHrTLceb8vB7u30GFXr-1csGQMUpnhQM6jC6jH6zVDjlYZ4jOHK2KJVK0LhQgYlM8BYbiY0Dx_gDzXjhB:1lBxcg:z1wg3bIhoeGG4C68lp4P64c-jhWQzpC2nFZt4zE8WAk	2021-03-02 13:30:26.5025+03
\.


--
-- Data for Name: main_domain; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_domain (name, age, unique_backlinks, total_backlinks, status) FROM stdin;
yandex.ru	10	533298	1704001746	complete
wikipedia.org	10	93223	1105535028	complete
youtube.com	10	15251885	2147483647	complete
7ya.ru	10	3749	225067	complete
womanadvice.ru	10	5470	197584	complete
nsportal.ru	10	6777	917263	complete
newslab.ru	10	5442	495257	complete
wikihow.com	10	153792	21723221	complete
bandaumnikov.ru	8	317	20350	complete
i-igrushki.ru	9	227	53067	complete
u-mama.ru	10	2546	59772	complete
pustunchik.ua	5	1098	10230	complete
babudacha.ru	5	127	1304	complete
maam.ru	10	2882	304928	complete
iigry.ru	2	12	25	complete
arhlive.ru	8	27	108	complete
imom.me	2	172	2009	complete
inteltoys.ru	10	600	28175	complete
uprostim.com	2	42	115	complete
shkolala.ru	5	190	1531	complete
2gis.ru	10	30371	16100495	complete
ayzdorov.ru	10	2016	65123	complete
reso.ru	10	2273	84183	complete
ingos.ru	10	3931	1435007	complete
ferma.expert	2	241	3685	complete
fructberry.ru	2	93	966	complete
floristics.info	6	437	3771	complete
oum.ru	10	1320	13498	complete
Sravni.ru	10	3724	165044	complete
absolutins.ru	5	641	398764	complete
kp.ru	10	29929	14234229	complete
pikabu.ru	10	20506	1510865	complete
depositphotos.com	10	31471	16701091	complete
BigPicture.ru	10	8368	923110	complete
BipBap.ru	5	695	17225	complete
yandex.com	10	47999	48269368	complete
instagram.com	10	10787773	2147483647	complete
vokrugsada.ru	5	117	604	complete
polzaed.ru	2	21	41	complete
soglasie.ru	10	1964	623459	complete
rastenievod.com	4	644	115215	complete
agroportal.online	3	42	278	complete
fruktopedia.ru	1	2	2	complete
gastronom.ru	10	2574	113897	complete
renins.ru	10	482	15802	complete
edaplus.info	10	1070	18914	complete
AlfaStrah.ru	10	3228	117500	complete
banki.ru	10	12479	1066315	complete
FoodandHealth.ru	7	567	15031	complete
zoon.ru	10	14346	26377185	complete
vbr.ru	10	1787	47416	complete
ydoo.info	2	114	913	complete
kaifolog.ru	10	1282	55500	complete
wiki2.org	6	3881	294866	complete
zvuch.com	0	63	3616	complete
vk.com	10	1050077	2147483647	complete
pixabay.com	10	216966	31819305	complete
megapesni.com	8	95	2422	complete
rutube.ru	10	36819	10570218	complete
ekabu.ru	10	2104	41842	complete
fishki.net	10	21709	2736200	complete
hitmo.me	1	89	736	complete
polzavred-edi.ru	1	127	7530	complete
Consultant.ru	10	46628	12811382	complete
cbr.ru	10	21406	7934856	complete
kfh-fruktovyjsad.ru	1	36	144	complete
bankiros.ru	5	1689	49301	complete
RGS.ru	10	4042	737974	complete
vsk.ru	10	2593	257272	complete
sberbank.ru	10	23454	4839257	complete
abri-kos.ru	9	122	429	complete
mail.ru	10	251301	1023724448	complete
goodgame.ru	10	10077	11791870	complete
wowjp.net	10	509	5998	complete
dota2.ru	10	2431	51972	complete
goha.ru	10	1360	891108	complete
hearthstone-like.ru	5	34	130	complete
allmmorpg.ru	8	104	829	complete
sports.ru	10	13344	6910089	complete
blizzard.com	10	15517	15529009	complete
playblizzard.com	2	54	205	complete
guideswow.ru	9	252	787	complete
hearthstone-game.ru	2	12	23	complete
thisgame.ru	5	34	101	complete
hs-manacost.ru	5	355	3355	complete
hsstats.ru	1	3	81	complete
kolodahearthstone.ru	4	27	728	complete
hsreplay.net	4	715	26055	complete
HearthStone-club.ru	7	36	102	complete
hsbaza.com	4	1	1	complete
wow-cool.ru	1	276	960	complete
syoutube.ru	2	84	905	complete
ok.ru	10	220178	721377598	complete
zonatarkova.ru	2	11	4701	complete
pressball.by	10	2038	197435	complete
topdeckmaster.ru	6	17	62	complete
natpagle.ru	7	46	295	complete
hearthgid.com	3	14	37	complete
play-hs.com	1	2	12	complete
1avtozvuk.ru	5	240	9783	complete
HoroshijPotolok.ru	4	53	1375	complete
окнотех.рф	10	115	304	complete
oknamaster.ru	10	337	1377	complete
fabrikaokon.ru	10	670	3856	complete
mosokna.ru	10	556	4439	complete
okna.ru	10	581	7600	complete
LeroyMerlin.ru	10	3464	582877	complete
Plastok.ru	10	202	1011	complete
oknastar.ru	10	176	2492	complete
psmith.ru	6	35	120	complete
oknober.ru	2	182	663	complete
fabrika-potolkov.ru	10	26	55	complete
23okna.ru	10	115	234	complete
design-okno.ru	10	54	169	complete
OKNO.ru	10	237	6034	complete
moscowbalkon.ru	4	69	130	complete
rukimastera.ru	10	29	69	complete
okna-servise.com	10	48	140	complete
veka.ru	10	957	67542	complete
oknamr.ru	3	24	70	complete
star-potolok.ru	7	95	2594	complete
rumexpert.ru	6	65	463	complete
студия-нп.рф	3	26	5462	complete
natjazhnye-potolki.su	7	29	101	complete
potolokmodern.ru	5	48	2488	complete
oknagorizont.ru	10	27	51	complete
nat-com.ru	10	59	219	complete
vipceiling.ru	10	481	2672	complete
okna-zavod.com	2	18	25	complete
potolkoff.ru	10	123	127390	complete
profi.ru	10	2025	1555532	complete
vtbins.ru	10	1413	466890	complete
mos.ru	10	18617	15806362	complete
tinkoff.ru	10	11061	2192412	complete
calcus.ru	6	670	494547	complete
otzovik.com	10	10773	1529570	complete
makc.ru	10	1321	25214	complete
driver-helper.ru	5	197	6768	complete
renlife.ru	10	331	3754	complete
ru.com	10	80	1284	complete
irecommend.ru	10	9284	742687	complete
sberbank-ru.ru	2	46	195	complete
asn-news.ru	10	2984	209158	complete
rg.ru	10	54786	15603547	complete
vash-potolok.ru	10	298	839	complete
mypotolok.ru	8	8	193	complete
ameliawork.ru	10	147	4424	complete
sovcomins.ru	0	259	3944	complete
epicris.ru	2	126	2519	complete
rsa.su	2	134	790	complete
allianz.ru	10	1018	9902	complete
sberbank-insurance.ru	8	420	467861	complete
strahov-ka.ru	4	4	7	complete
sbank-strahovka.ru	1	4	577	complete
osagonline.ru	2	251	874	complete
rshbins-life.ru	3	47	8036	complete
Strahovka.ru	10	205	984	complete
kaplife.ru	2	465	13132	complete
rosstrah.ru	2	180	1658	complete
OnlineStrah.ru	0	426	3219	complete
acko.ru	10	169	1265	complete
belta.by	10	11167	5639698	complete
proza.ru	10	12230	1731814	complete
warheroes.ru	10	3226	259204	complete
losik.ru	10	90	14883	complete
tvzvezda.ru	10	14407	3788579	complete
varlamov.ru	9	6633	307783	complete
litres.ru	10	13499	23101624	complete
tankfront.ru	10	544	28624	complete
rambler.ru	10	9853	8206147	complete
mil.ru	10	2827	867358	complete
academic.ru	10	23186	1334300	complete
tass.ru	10	59907	14195711	complete
livemaster.ru	10	9976	3526337	complete
ria.ru	10	80137	25859758	complete
histrf.ru	7	8304	18389306	complete
culture.ru	10	8982	10956847	complete
stuki-druki.com	6	1213	22582	complete
biographe.ru	3	650	3643	complete
uznayvse.ru	10	3875	199544	complete
24smi.org	10	4556	1121667	complete
ivi.ru	10	9141	3207914	complete
rustars.tv	3	135	2209	complete
kinopoisk.ru	10	26437	7588168	complete
kino-teatr.ru	10	6236	474361	complete
livejournal.com	10	63386	170357362	complete
lurkmore.to	5	9772	976041	complete
my-shop.ru	10	4594	4251006	complete
4lapy.ru	10	823	21377	complete
WildBerries.ru	10	9044	2828491	complete
OZON.ru	10	35957	19689703	complete
detmir.ru	10	2966	307286	complete
zapovednik96.ru	7	471	36176	complete
multikorm.ru	10	209	1609	complete
auchan.ru	10	2393	244640	complete
zoo-galereya.ru	10	201	4629	complete
bethowen.ru	10	978	24392	complete
unizoo.ru	8	297	5254	complete
MagiZoo.ru	7	239	8852	complete
petshop.ru	10	944	16113	complete
goods.ru	10	1453	132284	complete
ZooPassage.ru	8	291	28963	complete
DogEat.ru	10	364	14125	complete
mirkorma.ru	10	369	1655	complete
zoomag.ru	10	164	11470	complete
petfood.ru	10	75	4684	complete
zooidea.ru	7	51	234	complete
vyboroved.ru	9	616	6326	complete
satom.ru	9	2512	1168136	complete
ZooSell.com	7	175	1059	complete
zoostore.pro	1	38	190	complete
mirpopugaev.ru	0	7	15	complete
parrotsworld.ru	2	48	300	complete
4parrots.ru	9	89	1197	complete
lubimchik.ru	9	214	4919	complete
happybirds.ru	9	54	907	complete
whiteprofit.ru	9	130	1149	complete
iklife.ru	6	1023	35284	complete
myrouble.ru	10	645	5984	complete
skillbox.ru	7	1480	32844	complete
netology.ru	10	2923	489869	complete
law03.ru	5	370	4664	complete
workinnet.ru	2	101	246	complete
sposob-zarabotat.ru	2	69	127	complete
kadrof.ru	10	829	3504	complete
vc.ru	10	13336	1138213	complete
BiznesSystem.ru	10	430	2964	complete
beboss.ru	10	1602	314758	complete
Horhi.ru	1	1	1	complete
businessmens.ru	7	384	38063	complete
hostinger.ru	10	958	19689	complete
AWayne.biz	2	64	285	complete
denezhnye-ruchejki.ru	4	60	186	complete
mynetmoney.ru	6	204	2321	complete
ifish2.ru	5	855	34794	complete
web-copywriting.ru	8	73	3037	complete
shard-copywriting.ru	10	433	6757	complete
misterrich.ru	4	64	3376	complete
job-opros.ru	3	973	71383	complete
internet-technologies.ru	10	1292	23367	complete
infinitymoneyonline.com	4	158	422	complete
webmoney-rabota.ru	8	59	112	complete
content-online.ru	2	96	661	complete
SlonoDrom.ru	4	113	11230	complete
pammtoday.com	8	292	3065	complete
FinFocus.today	3	136	263	complete
DomClick.ru	4	3241	790222	complete
blogspot.com	10	619372	2147483647	complete
BezFormata.com	9	9687	1313973	complete
46tv.ru	9	1173	21663	complete
kpravda.ru	10	912	30821	complete
tvoyadres.ru	10	370	131680	complete
gorenka.org	7	163	3026	complete
egrp365.ru	5	950	109684	complete
KurskMetr.ru	10	226	758	complete
geodzen.com	2	33	259	complete
street-viewer.ru	7	49	1978	complete
youkarta.ru	3	65	295	complete
city-address.ru	5	54	131	complete
russia-karts.ru	3	48	67	complete
bestmaps.ru	10	395	7534	complete
wikichi.ru	0	47	281	complete
sport24.ru	3	2781	336543	complete
championat.com	10	13355	5309220	complete
fclmnews.ru	7	195	2340	complete
soccer.ru	10	1950	1152889	complete
soccer365.ru	10	1688	82485	complete
fclm.ru	10	1957	1616714	complete
transfermarkt.ru	10	635	50508	complete
premierliga.ru	10	956	517500	complete
matchtv.ru	5	7009	2808478	complete
sport-express.ru	10	8991	3954470	complete
sportbox.ru	10	8500	2839725	complete
Avito.ru	10	18017	13202661	complete
cian.ru	10	3412	317786	complete
labirint.ru	10	11682	10820954	complete
aif.ru	10	33867	20812991	complete
tripadvisor.ru	10	13194	6707938	complete
yandex.by	10	9815	7116001	complete
MoscowMap.ru	10	846	13600	complete
msk.ru	10	2111	80134	complete
fandom.com	10	10359	9866123	complete
turbina.ru	10	1394	145920	complete
mwmoskva.ru	6	668	6105338	complete
deriglazovo.ru	5	11	113	complete
deriglazova.com	2	-1	-1	complete
zavodkpd.ru	10	52	374	complete
realtyse.net	10	215	1143	complete
dns-shop.ru	10	7192	351365	complete
umka.org	10	198	593	complete
mosmetro.ru	10	1643	24943	complete
MosOpen.ru	10	1147	116749	complete
mskof.ru	4	27	108	complete
MetroBook.ru	10	50	190	complete
shema-metro-moskva.ru	2	11	55	complete
nashtransport.ru	10	272	4497	complete
4pda.ru	10	13513	2234594	complete
kartaslov.ru	3	1023	1077540	complete
diletant.media	5	2186	103166	complete
coronavirus-monitor.ru	0	1860	233888	complete
chitai-gorod.ru	10	2926	166659	complete
tjournal.ru	9	10789	510887	complete
1tv.ru	10	36395	3292461	complete
zhazhdazolota.ru	2	43	108	complete
google.com	10	9967668	2147483647	complete
naked-science.ru	8	4956	240218	complete
SetPhone.ru	8	338	4442	complete
ren.tv	10	14595	1718789	complete
gazeta.ru	10	34642	7088780	complete
dobro-est.com	10	1345	30079	complete
9111.ru	10	3911	361642	complete
iz.ru	10	43094	6658637	complete
bolshoyvopros.ru	10	4401	648722	complete
noob-club.ru	10	726	57390	complete
habr.com	10	31561	12240029	complete
rbc.ru	10	45414	11511535	complete
ixbt.com	10	13492	24308977	complete
KrasotaiMedicina.ru	10	1558	91000	complete
covid-stat.com	0	40	115	complete
telesputnik.ru	10	3325	184890	complete
drive2.ru	10	15897	14660178	complete
coronavirus-monitor.info	0	464	890653	complete
coronavirus-control.ru	0	570	61527	complete
e-katalog.ru	10	5095	7196009	complete
ushistory.ru	10	256	936	complete
discoverychannel.ru	10	642	12690	complete
zolotoy-zapas.ru	10	92	113201	complete
mosgorzdrav.ru	10	4448	1265766	complete
mvideo.ru	10	6529	427923	complete
wowhead.com	10	12245	14777810	complete
rosminzdrav.ru	10	18405	36301156	complete
dtv.plus	0	5	6731	complete
ncov.blog	0	61	628	complete
goldlode.ru	7	48	130	complete
chinese-projectors.ru	1	32	123	complete
zona.plus	2	464	135805	complete
koronavirus-today.ru	0	53	166	complete
android.com	10	46819	5641050	complete
стопкоронавирус.рф	0	9957	9802236	complete
tvdroid.ru	4	77	372	complete
webhalpme.ru	2	122	885	complete
LordFilms-s.pw	1	119	783	complete
citilink.ru	10	4251	1289356	complete
nlv.ru	10	225	20978	complete
lasik.ru	10	238	1628	complete
proglazki.ru	2	113	2141	complete
elitplus-clinic.ru	3	81	690	complete
fedorovmedcenter.ru	10	435	6085	complete
vseozrenii.ru	10	208	934	complete
cvz.ru	10	291	1083	complete
mgkl.ru	9	887	4463	complete
ProDoctorov.ru	9	3344	2703594	complete
spid.center	5	792	92232	complete
lensmaster.ru	10	680	19949	complete
doctor-shilova.ru	10	125	1919	complete
operaciya.info	4	222	1732	complete
napopravku.ru	10	882	124367	complete
excimerclinic.ru	10	1037	11637	complete
ochkov.net	10	1422	15575	complete
103.by	10	1426	149606	complete
lazernaya-korrekciya-zreniya.ru	0	33	62	complete
emcmos.ru	10	1222	66608	complete
medicina.ru	10	860	30050	complete
kiz.ru	10	767	34773	complete
celt.ru	10	672	5956	complete
sfe.ru	10	326	1584	complete
auto.ru	10	9491	8298035	complete
domofond.ru	10	1702	95741	complete
multilisting.su	8	275	23790	complete
irr.ru	10	7454	287774	complete
kvartelia.ru	3	60	152	complete
sob.ru	10	1475	91824	complete
novostroy.ru	10	631	677773	complete
avaho.ru	6	391	10864	complete
kupiprodai.ru	10	1513	4289713	complete
realtymag.ru	10	466	38922	complete
move.ru	10	937	121779	complete
Novostroy-m.ru	9	1018	711464	complete
drom.ru	10	3590	472433	complete
mirkvartir.ru	10	1307	12566	complete
AutoSpot.ru	10	401	3795	complete
wiweb.ru	10	356	9705	complete
quto.ru	10	1985	116833	complete
avtomir.ru	10	1098	197767	complete
youla.ru	10	2716	634249	complete
N1.ru	10	64	1157	complete
Etagi.com	10	630	4841	complete
rolf.ru	10	929	956462	complete
favorit-motors.ru	10	802	126824	complete
m2.ru	10	446	11762	complete
CarsDo.ru	7	78	926	complete
autograd-m.ru	10	123	402	complete
rolf-probeg.ru	2	639	174318	complete
AvtoGermes.ru	10	1632	40097	complete
Major-Expert.ru	10	674	125538	complete
egsnk.ru	10	354	11037	complete
avilon.ru	10	877	18471	complete
saloncentr.ru	10	633	4467	complete
masmotors.ru	10	673	35245	complete
major-auto.ru	10	828	131225	complete
zrenie-gid.ru	2	5	7	complete
glaza.help	2	112	774	complete
glaz-kursk.ru	10	19	40	complete
oko-kursk.ru	5	8	27	complete
meddoclab.ru	2	603	2759	complete
happylook.ru	10	747	8495	complete
Biglion.ru	10	2128	278230	complete
blizko.ru	10	2255	152666	complete
big-book-med.ru	8	2	3	complete
DOCTU.ru	7	329	15957	complete
facebook.com	10	25694238	2147483647	complete
zrenie46.ru	1	6	13	complete
36n6.ru	8	89	202	complete
ophthalmology.top	3	207	9132	complete
tiu.ru	10	27799	71189703	complete
galamart.ru	10	962	70003	complete
sima-land.ru	10	3438	2731866	complete
moi-tvoi.ru	6	570	2675	complete
ikea.com	10	127908	12139667	complete
twitter.com	10	16857359	2147483647	complete
lokomotiv.info	10	743	7033	complete
cskamoskva.ru	10	1191	31970	complete
supl.biz	7	242	9331	complete
vintajj.ru	10	68	221	complete
umslon.ru	2	104	394	complete
mineralmarket.ru	9	330	79367	complete
zontshop.ru	10	248	1014	complete
podarki-market.ru	10	121	1925	complete
goods-club.ru	6	179	1040	complete
statuetka.shop	1	2	2	complete
football-cska.com	1	1	2	complete
pfc-cska.com	10	2362	657725	complete
football24.ru	10	271	8182	complete
cskanews.com	9	468	2395	complete
znak.com	10	9216	1072560	complete
supernovum.ru	6	243	314531	complete
aeternamemoria.ru	2	78	382	complete
business-gazeta.ru	10	8057	755997	complete
altapress.ru	10	5175	2038470	complete
svpressa.ru	10	10498	866322	complete
life.ru	10	19635	1680644	complete
supremusdies.info	2	11	29	complete
tonkosti.ru	10	7290	970165	complete
KitayGid.ru	2	150	692	complete
tourister.ru	10	4236	1235717	complete
chinahighlights.ru	10	143	1985	complete
make-trip.ru	7	307	18669	complete
avbessonov.ru	2	42	1212	complete
34travel.me	4	1662	30785	complete
OneTwoTrip.com	10	1650	43925	complete
life-like-travel.ru	7	38	466	complete
GuruTurizma.ru	6	247	3574	complete
SiteKid.ru	9	160	976	complete
putihod.ru	2	42	244	complete
SpiritRelax.ru	6	123	925	complete
ChinaExpro.ru	5	95	410	complete
iamcook.ru	10	892	50443	complete
RussianFood.com	10	3528	391980	complete
koolinar.ru	10	1550	131579	complete
povar.ru	10	3866	599762	complete
gotovim-doma.ru	10	1874	42570	complete
eda.ru	10	1836	518103	complete
povarenok.ru	10	4715	1136253	complete
afisha.ru	10	8127	784225	complete
1000.menu	6	1052	483764	complete
restoclub.ru	10	1509	20385	complete
bash.today	6	171	2104	complete
mykitai.ru	4	75	300	complete
jj-tours.ru	7	343	5344	complete
studychinese.ru	10	236	2610	complete
showasia.ru	8	138	4475	complete
tonmeta.com	3	16	58	complete
ucoz.ru	10	17457	42261524	complete
ichinese.online	3	24	45	complete
mirtesen.ru	10	36533	134564202	complete
yesasia.ru	10	527	89536	complete
spletnik.ru	10	5204	868841	complete
4tololo.ru	8	2027	73405	complete
laowai.ru	10	218	1446	complete
prc.today	1	25	536	complete
qaz.wiki	0	3190	107960	complete
laovaev.net	5	61	205	complete
ekd.me	5	706	49359	complete
jobvnet.ru	2	73	313	complete
ivitop.ru	4	14	151	complete
ZarabotkiOnline.ru	4	97	1174	complete
adbz.ru	2	40	107	complete
kakzarabotat.net	6	121	323	complete
zarabotok-na-buksakh.ru	1	322	16350	complete
workion.ru	7	251	1200	complete
RealnyeZarabotki.com	5	197	1547	complete
VadimMorozov.ru	1	44	78	complete
onlaines.com	2	36	124	complete
monetacar.org	2	36	78	complete
iprodvinem.ru	4	69	1653	complete
seosprintwork.ru	0	6	21	complete
RealZarabotok.com	4	51	244	complete
investbro.ru	5	458	21607	complete
finova.ru	6	22	547	complete
super-blog.ru	1	58	359	complete
firelinks.ru	6	130	802	complete
SkillBlog.ru	2	22	30	complete
opros.io	2	20	165	complete
bizsovet.com	1	49	64	complete
livesurf.ru	9	1309	352904	complete
internetboss.ru	3	229	525	complete
bobsoccer.ru	10	1102	83851	complete
platnye-oprosy.ru	2	34	56	complete
1000rabota.ru	4	300	17375	complete
platnye-oprosi.ru	4	88	509	complete
gain-profit.com	4	114	224	complete
otdyhsamostoyatelno.ru	3	105	37655	complete
vsvoemdome.ru	3	244	4050	complete
prosto-eto.ru	2	19	44	complete
Delen.ru	6	176	5349	complete
heaclub.ru	5	773	10334	complete
MirF.ru	10	2419	662352	complete
capitalgains.ru	5	226	928	complete
24tv.ua	5	12259	2299098	complete
gq-blog.com	0	507	140287	complete
anews.com	10	3096	57444	complete
profvest.com	6	982	360673	complete
SilaMira.ru	2	41	118	complete
lifestyledigital.ru	2	38	157	complete
bizec.ru	1	38	74	complete
MilitaryArms.ru	6	939	8717	complete
kommersant.ru	10	50745	9406561	complete
ukraina.ru	10	3732	255458	complete
obozrevatel.com	10	12892	2070833	complete
meduza.io	6	21646	3771035	complete
lenta.ru	10	46865	18244886	complete
strana.ua	5	8393	960338	complete
bbc.com	10	442246	65738199	complete
WarWays.ru	3	112	1217	complete
GruziyaGid.ru	2	108	728	complete
topwar.ru	10	9200	1968335	complete
openbusiness.ru	10	914	42179	complete
dohodinet.ru	3	105	5969	complete
domznaniy.info	6	80	275	complete
seo-town.ru	2	43	683	complete
investobox.ru	6	22	25	complete
wikirabota.ru	2	14	97	complete
infozet.ru	1	37	57	complete
Albakoff.ru	3	75	2103	complete
vipidei.com	6	112	783	complete
wikiquote.org	10	1140	119428	complete
kupidonia.ru	8	378	8628	complete
moiposlovicy.ru	4	32	47	complete
diktory.com	9	161	504	complete
schci.ru	3	51	194	complete
net.ru	10	500	867346	complete
pogovorki-poslovicy.ru	9	29	317	complete
multi-mama.ru	1	79	808	complete
goldenwords.org	8	49	437	complete
iamruss.ru	7	220	986	complete
skazka-dubki.ru	8	188	793	complete
hobobo.ru	10	789	32530	complete
poslovitza.ru	8	84	314	complete
notagram.ru	4	179	663	complete
nickdegolden.ru	7	81	212	complete
folkmir.ru	2	20	26	complete
booksite.ru	10	2601	89200	complete
folklora.ru	4	17	130	complete
russkie-poslovitsi.ru	7	7	18	complete
dslov.ru	8	299	1527	complete
liveinternet.ru	10	100788	2147483647	complete
i.ua	5	6162	58378783	complete
sayings.ru	10	11	48	complete
BBF.ru	4	901	23477	complete
stihi.ru	10	15269	2460765	complete
litfest.ru	1	233	3637	complete
jofo.me	4	2	5	complete
citaty.su	10	371	5173	complete
orator.ru	10	619	2872	complete
poslovic.ru	4	21	37	complete
detochki-doma.ru	9	474	1606	complete
refleader.ru	6	202	748	complete
studbooks.net	7	967	8983	complete
com.ua	5	139	4140	complete
microsoft.com	10	1045506	419428708	complete
wb0.ru	10	256	6294	complete
pfrf.ru	10	14392	20128223	complete
itnan.ru	5	153	2217	complete
infostart.ru	10	1987	6666592	complete
webznam.ru	8	146	989	complete
diadoc.ru	10	1431	90922	complete
software-testing.ru	10	870	37155	complete
coderlessons.com	1	192	8648	complete
pbprog.ru	10	2481	4324648	complete
quizful.net	10	553	2686	complete
academiait.ru	3	180	122614	complete
BuhSoft.ru	10	940	10533	complete
veralsoft.com	10	11	32	complete
wtools.io	4	215	4587	complete
way23.ru	3	5	126	complete
medoblako.ru	8	168	746	complete
3z.ru	10	140	2191	complete
eyesurgerycenter.ru	8	80	598	complete
vseosmile.ru	3	6	11	complete
optic-center.ru	10	127	2290	complete
glazaizrenie.ru	3	67	704	complete
proektpro.su	1	15	24	complete
houzz.ru	10	3532	2029336	complete
potolok-magazin.ru	6	49	6762	complete
potolki-natyagnye.ru	4	165	892	complete
potolokmoscow.ru	9	18	46	complete
potolok-stail.ru	10	411	3348	complete
LivePosts.ru	5	271	2926	complete
vse-kursy.by	5	120	2352	complete
duolingo.com	10	35325	2072542	complete
vesti.ua	5	10379	662277	complete
uchiyaziki.ru	10	520	1591	complete
wday.ru	10	4418	484101	complete
4mama.ua	5	572	204239	complete
funeasylearn.com	8	344	3217	complete
loecsen.com	10	1888	127799	complete
bookland.com	10	783	14436	complete
17-minute-languages.com	7	792	3160553	complete
lingohut.com	10	724	727407	complete
legkonauchim.ru	1	53	402	complete
50languages.com	10	1093	87259	complete
firmika.ru	7	504	187871	complete
tatueskiz.ru	2	69	629	complete
tattooz.ru	10	315	1032	complete
jtattoo.ru	5	6	7	complete
YouDo.com	10	1874	2152806	complete
spicytattooing.ru	2	4	6	complete
skolkos.ru	5	157	586	complete
TattooClassic.ru	2	42	109	complete
SyndicateTattoo.ru	3	32	159	complete
empiretattoo.ru	10	126	544	complete
vse-o-tattoo.ru	7	332	7085	complete
crazytattoo.ru	8	109	743	complete
minitatts.ru	1	-1	-1	complete
tattoomoscow.ru	10	143	347	complete
kottattoo.ru	4	47	91	complete
tattoorus.ru	6	71	531	complete
vivotattoo.com	3	3	4	complete
chilloutworkshop.com	7	13	19	complete
krace.ru	10	514	20465	complete
TattooDragon.ru	10	120	488	complete
club-tattoo.ru	1	131	9837	complete
tattoonaive.ru	0	1	1	complete
ArtOfPain.ru	7	110	256	complete
themoodmagazine.ru	4	31	101	complete
lacutetattoo.ru	0	9	31	complete
pigmentlab.ru	3	9	12	complete
punktirtattoo.ru	3	33	41	complete
TattooMall.ru	6	102	354	complete
darbytattoo.ru	0	-1	-1	complete
startattoo.ru	3	12	119	complete
tattooa.ru	9	37	253	complete
tattoo-77.ru	7	117	629	complete
tatu-shop.ru	5	12	30	complete
tattoo82.ru	2	20	64	complete
krasotkapro.ru	9	884	38212	complete
KittyFace.ru	4	35	95	complete
kurer-sreda.ru	10	3273	807815	complete
locatus.ru	5	161	2675	complete
69level.com	10	89	5010	complete
ellittattoo.ru	10	242	608	complete
MyBeauty.pro	5	154	510	complete
msk-beauty.ru	10	200	10628	complete
NeedSpec.ru	3	49	151	complete
cheros.ru	6	30	87505	complete
hipdir.com	5	487	23014	complete
piercingmarket.ru	10	34	12748	complete
epilstudio.ru	8	6	206	complete
all4tattoo.ru	9	24	56	complete
freak-butik.ru	7	11	29	complete
pirsa.ru	1	0	0	complete
gidtattoo.ru	0	33	524	complete
rocknshop.ru	10	71	310	complete
joom.com	10	1908	232743	complete
ebay.com	10	245309	501747441	complete
BlackRiverStore.ru	3	32	42	complete
piersingshop.ru	2	0	0	complete
sokolov.ru	10	760	50558	complete
AliExpress.ru	10	6703	770570	complete
piercing.wiki	1	8	30	complete
40nog.ru	2	457	1225	complete
topgrant.ru	10	259	2662	complete
vestor-ru.ru	2	740	83136	complete
wanna-be.ru	8	50	1475	complete
PirsingTattoo.ru	3	11	19	complete
compumir.ru	2	931	8889	complete
alibaba.com	10	78971	32295396	complete
Sunlight.net	7	7926	614208	complete
tattooha.com	10	415	1436	complete
pinterest.ru	5	19729	25972096	complete
LadyKiss.ru	10	401	1702	complete
lifegirl.ru	4	203	2552	complete
x-tattoo.ru	1	29	114	complete
gerdanka.ru	1	120	1281	complete
afmen.online	3	183	980	complete
tatuirovanie.ru	10	291	944	complete
uniquetattoo.ru	6	123	631	complete
wikiw.life	2	174	1206	complete
almode.ru	6	112	1106	complete
ratatum.com	4	425	96111	complete
tattoofan.ru	3	51	317	complete
mysekret.ru	5	490	20407	complete
tattoo-masters.com	3	20	29	complete
tatuxa.com	1	26	690	complete
wowtrends.ru	1	6	18	complete
myglamour.ru	2	42	794	complete
tattoo-sketches.com	3	67	428	complete
slovami.net	3	326	4336	complete
DrawInks.com	6	196	1117	complete
cosmo.ru	10	8332	357515	complete
tattoo-ideas.ru	3	29	180	complete
2orto.ru	5	110	1404	complete
DomDivanov.moscow	4	4	40	complete
steepmen.ru	1	13	121	complete
MebelVia.ru	7	538	391320	complete
OGOGO.ru	10	700	294553	complete
MarketPik.ru	9	14	57	complete
pressa.tv	9	1194	122921	complete
InMyRoom.ru	9	2207	84526	complete
moltobene.su	5	-1	-1	complete
adme.ru	10	17550	1087711	complete
tattoofresh.ru	2	41	286	complete
krot.info	3	408	12462	complete
erekto.ru	1	53	307	complete
otattu.ru	3	33	174	complete
toptattoo.ru	10	53	208	complete
onedio.ru	6	1189	220328	complete
intrigue.dating	5	395	2241	complete
kissmytattoo.ru	6	69	265	complete
news-ontime.ru	5	71	619	complete
FB.ru	10	11023	747912	complete
on-tattoo.ru	4	79	495	complete
flakonn.com	3	73	1304	complete
tattootut.ru	2	5	9	complete
krasotka.cc	4	476	23997	complete
trinixy.ru	10	6544	223467	complete
zagony.ru	10	1330	40085	complete
samiysok.com	5	283	1723	complete
ledixbeauty.ru	3	116	492	complete
mixfacts.ru	7	424	5127	complete
barb.ua	5	727	12096	complete
westendstudio.ru	9	99	225	complete
obereginfo.ru	2	25	99	complete
avrorra.com	4	356	7316	complete
skarletta.ru	7	103	312	complete
tattoo-love.ru	0	495	9962	complete
ttattu.ru	1	4	4	complete
tattooassist.com	2	28	205	complete
bnti.ru	10	403	10302	complete
day.az	5	1629	1443409	complete
caitik.ru	5	336	1186	complete
novate.ru	5	5341	601517	complete
muzcina.ru	5	96	483	complete
biglion.ru	10	2154	282772	complete
protatuazh.ru	5	16	38	complete
uslugio.com	4	123	5658	complete
poisk-mastera.ru	8	90	676	complete
eselevich.com	6	44	158	complete
facultetkrasoti.ru	2	19	61	complete
KudaGid.ru	3	49	3169	complete
LikeFifa.ru	8	278	1447	complete
sm-estetica.ru	8	179	12865	complete
Stilistic.ru	10	109	1549	complete
thelashes.ru	5	104	295	complete
myguru.ru	5	91	383	complete
estelab.ru	10	147	34317	complete
elle-permanent.ru	3	16	227	complete
eyes-n-lips.ru	9	39	246	complete
permanent-moscow.ru	2	11	26	complete
artatoo.ru	10	33	349	complete
pinkmarket.ru	10	108	517	complete
tatuaj-moskva.ru	3	5	5	complete
Tattoo-Marilyn.ru	10	75	977	complete
pm-great.ru	1	5	8	complete
sphinxpm.ru	3	59	254	complete
barb.ru	9	253	975	complete
krasota.guru	4	162	1056	complete
Yell.ru	10	4558	2480169	complete
sanata-s.ru	10	162	955	complete
trade-services.ru	6	43	6010	complete
citynails.studio	3	26	143	complete
revival-clinic.ru	8	56	565	complete
anna-key.ru	7	47	252	complete
home-tatu.ru	5	46	87	complete
medkompas.ru	10	520	13836	complete
tatler.ru	10	1940	115401	complete
BioKrasota.ru	10	467	1646	complete
liontattoostudio.com	6	52	165	complete
tatuazh-spb.ru	6	13	40	complete
tattoo-pro.ru	10	109	595	complete
kleos.ru	10	679	9374	complete
eriton.ru	3	3	3	complete
moiprofi.ru	6	111	11801	complete
studio-bsi.ru	3	3	4	complete
StokDivanov.ru	10	394	2148	complete
alfamart24.ru	7	90	2981	complete
dubrava.net	2	0	0	complete
regmarkets.ru	7	1347	120061	complete
MrDivanoff.ru	3	72	45853	complete
MnogoMeb.ru	10	478	2977	complete
nonton.ru	7	194	1094	complete
rattan-mebel.ru	10	51	121	complete
mallmebeli.ru	0	159	484	complete
berkleyhome.ru	2	212	270	complete
anderssen.ru	10	638	8772	complete
saledivan.ru	4	8	11	complete
MnogoDivanov.ru	8	175	9491	complete
americanfurniture.ru	6	-1	-1	complete
mebHOME.ru	10	338	346482	complete
SkDesign.ru	9	165	2676	complete
matras.ru	10	508	6481	complete
mebelny-dom.com	7	133	434	complete
uglovye-divaniy.ru	5	35	146	complete
divano.ru	10	555	12171	complete
berkem.ru	4	953	27042	complete
HomeMe.ru	9	745	62402	complete
divanchik.org	10	74	325	complete
mebel-today.ru	10	141	1082	complete
Angstrem-mebel.ru	10	898	412382	complete
zvet.ru	10	802	37179	complete
mebel-top.ru	10	511	54593	complete
rasprodaza-divanov.ru	5	119	352	complete
sfera36.ru	7	57	660	complete
DG-home.ru	8	749	15341	complete
vdivan.ru	5	10	12	complete
vmk-mebel.ru	5	51	191	complete
filmebel.ru	5	223	1590	complete
tr-m.ru	5	0	0	complete
mebelidomanet.ru	5	160	318	complete
yavitrina.ru	5	771	9113	complete
komplektmeb.ru	5	1	1	complete
divanchik.ru	10	22	75	complete
stroy-podskazka.ru	5	494	35790	complete
dantonehome.ru	5	74	3202	complete
ecolmebel.ru	5	451	1636	complete
raskladushka.com	5	17	27	complete
divan78.ru	5	9	508	complete
ametist-store.ru	5	346	11973	complete
son-divan.ru	5	14	681	complete
askona.ru	10	1660	250578	complete
sosmebel.ru	5	13	31	complete
hoff.ru	5	1340	229710	complete
mirena-lider.ru	5	159	339	complete
RemDivana.ru	5	44	172	complete
propartner.ru	5	409	10176	complete
Mebel169.ru	4	310	15124	complete
moon-trade.ru	7	231	224310	complete
poztelio.com	2	63	469	complete
Krovat.ru	10	311	1742	complete
100fabrik.ru	10	372	3835	complete
gramercy-home.ru	7	101	3470	complete
basicdecor.ru	9	731	27658	complete
englishinteriors.ru	10	35	610	complete
sleepnation.ru	4	57	214	complete
raskladushkino.ru	3	0	0	complete
anatomiyasna.ru	8	1514	6457	complete
divani-i-krovati.ru	7	479	9876	complete
foto-designa.ru	1	20	112	complete
yyut.ru	5	5	22	complete
utro-vam.ru	7	289	644	complete
все-для-мебели.рф	10	37	105	complete
furnitura-ms.ru	3	3	3	complete
lamel66.ru	3	10	38	complete
mebelgroup.com	5	12	71	complete
italmc.ru	7	135	264	complete
gallereya.ru	10	365	2881	complete
mobilicasa.ru	5	649	4083	complete
grand-italia.ru	7	36	245	complete
abitant.com	10	304	1959	complete
union-mebel.ru	10	123	1950	complete
italmond.ru	8	34	75	complete
toriani.ru	5	28	135	complete
ital-moscow.ru	5	123	79608	complete
ardisdesign.ru	2	6	13	complete
classicomobili.ru	3	11	20	complete
ekspert-mebel.ru	7	125	26064	complete
italishop.ru	1	6	13	complete
blissinhome.com	7	152	284	complete
italmaniya.ru	9	135	2645	complete
mibele.ru	5	21	158	complete
lacasa-m.ru	10	285	882	complete
arredo.ru	10	338	1327	complete
lubidom.ru	9	822	10250	complete
ArmadiLux.ru	4	7	22	complete
blomer.ru	10	45	178	complete
italini.ru	8	109	1041	complete
mebelvnalichii.ru	5	21	120	complete
Elite-Moscow.ru	10	314	38208	complete
dizayndoma.com	5	128	11181	complete
italmebeltorg.ru	5	14	1344	complete
Belfan.ru	5	365	2289	complete
mobiliitalia.ru	5	71	271	complete
italianskaia-mebel.ru	9	193	569	complete
pm.ru	10	647	73938	complete
mebelmsk.ru	10	24	55	complete
mebelion.ru	10	1228	156009	complete
centr-mebel.com	4	71	158604	complete
meb-elite.ru	10	323	969	complete
nuzhna-mebel.ru	5	19	74	complete
mebelmod.ru	10	28	84	complete
good-mebel.ru	10	326	22084	complete
mebel-meridian.ru	10	201	372	complete
mebel-proffy.ru	10	235	248031	complete
antarescompany.ru	10	241	7767	complete
mebel-liberty.ru	5	55	164	complete
mebelevropa.ru	5	86	443	complete
LegkoMarket.ru	5	245	20188	complete
HouseDiz.com	5	178	482	complete
neopoliscasa.ru	5	470	106718	complete
ib-gallery.ru	5	91	5975	complete
avel-m.ru	5	270	826	complete
fmcomfort.ru	5	21	175	complete
100li.ru	5	69	130	complete
BarcelonaDesign.ru	5	94	721	complete
stolplit.ru	5	1429	135468	complete
BestMebelShop.ru	5	196	871	complete
mebel-Bruno.ru	5	28	4216	complete
LifeMebel.ru	5	554	24320	complete
mebel-na-rusi.ru	5	61	188	complete
GermanWorld.ru	10	103	431	complete
mebel-atrium.ru	10	58	364	complete
thefields.ru	6	140	93638	complete
milano-home.ru	10	87	454	complete
td-arnika.ru	10	686	60047	complete
meb-online.ru	10	289	1259	complete
IDCollection.ru	6	612	2769	complete
etagerca.ru	8	246	3307	complete
bme.sale	0	4	12	complete
homint.ru	3	205	2942	complete
MebelForte.ru	5	42	177	complete
alterego-mebel.ru	10	47	3993	complete
camelgroupmobili.ru	7	10	43	complete
cucine.ru	10	106	473	complete
lecucine.ru	8	53	134	complete
dorogie-kuhni.ru	5	46	59	complete
itacom.ru	10	77	2352	complete
mebelitalii.ru	10	159	388	complete
kuxni.net	10	251	3624	complete
ital-collection.ru	4	6	15	complete
gl-studio.com	9	59	115	complete
galaktika21.ru	10	127	420	complete
zorini.ru	2	42	75	complete
elegrum.ru	8	37	534	complete
idcucine.ru	0	14	17001	complete
kuhni-italy.ru	2	623	693	complete
mirkuhni.ru	10	63	285	complete
Aldas.ru	4	36	829	complete
westwing.ru	9	1020	4503	complete
kuhnimilana.ru	4	730	1446	complete
stolli.ru	3	7	11	complete
nedorogo-kuhni.ru	2	85	4399	complete
kuhnipriroda.ru	4	8	367	complete
tesoromebel.ru	6	653	20854	complete
kuhni-na-zakaz.pro	2	376	1797	complete
silverhome.design	3	85	434	complete
russans.ru	1	74527	15694873	complete
furnikuhni.ru	6	31	530	complete
mastermebius.ru	10	135	515	complete
Marya.ru	10	1023	276345	complete
KuhniPark.ru	10	136	348	complete
fkm-anons.ru	10	226	40974	complete
sofihome.ru	5	4	4	complete
1mf.ru	5	691	57619	complete
dizajnhome.ru	2	37	192	complete
kitcheninteriors.ru	10	75	1490	complete
stilecasa.ru	10	31	51	complete
tytdesign.info	1	18	121	complete
remont-f.ru	10	630	43880	complete
geometrium.com	7	301	2394	complete
dizainexpert.ru	3	207	2443	complete
Angelika-Prudnikova.design	3	75	5411	complete
dizainvfoto.ru	5	155	634	complete
mebel-mr.ru	10	331	51915	complete
reywood.ru	8	141	83504	complete
rdmkuhni.ru	5	27	64	complete
makonti.com	3	0	0	complete
vyborexperta.ru	3	415	3251	complete
IdealKitchen.ru	10	328	2789	complete
aaaclass.ru	5	20	57	complete
kehohome.ru	5	1	4	complete
KuhniDom.com	5	46	93	complete
maxlevel.ru	10	202	3218	complete
yellmed.ru	5	808	133699	complete
dentabravo.ru	9	53	114	complete
24stoma.ru	9	311	7275	complete
zub.ru	10	245	12005	complete
chudostom.ru	4	88	2141	complete
dantistoff.ru	8	101	27391	complete
siberianhealth.com	10	2225	136081	complete
stomatologclub.ru	10	315	4398	complete
klinika-abc.ru	10	577	3780	complete
32top.ru	10	493	2922	complete
StartSmile.ru	10	733	31835	complete
interdent.ru	10	5	62	complete
Dentserv.ru	10	107	345	complete
dentalgu.ru	10	635	13802	complete
me-dent.ru	5	167	512	complete
vivadent.moscow	5	317	1652	complete
stomatologicheskie-kliniki-moskvy.ru	3	62	99	complete
stom-info.ru	2	31	159	complete
stomatologija.su	10	258	7694	complete
profident.ru	10	110	206	complete
stomdom.com	5	84	114	complete
medikastom.ru	10	228	524	complete
legstom.ru	2	27	58	complete
novadent.ru	10	167	766	complete
zdravcity.ru	8	1910	181884	complete
fdoctor.ru	10	781	24715	complete
Vse-svoi.ru	10	522	4804	complete
sm-stomatology.ru	4	61	17761	complete
stom-firms.ru	10	270	3272	complete
lechenie-zub.ru	0	-1	-1	complete
stominmoscow.ru	1	38	129	complete
doctorzub.su	0	2	11	complete
orbital-dent.ru	1	23	343	complete
inwhite-medical.ru	4	36	534	complete
smile-std.ru	8	59	135	complete
polyclin.ru	5	254	9930	complete
stomatologi.moscow	5	43	139	complete
prezi-dent.ru	5	350	13693	complete
dentaliga.ru	5	78	391	complete
dentspecialist.ru	5	71	933	complete
kariesy.net	5	72	183	complete
imma.ru	10	159	1819	complete
DocDoc.ru	10	2011	647719	complete
dento-komfort.ru	10	14	68	complete
stomatorg.ru	10	126	4760	complete
cniis.ru	5	473	1952	complete
smclinic.ru	10	947	28802	complete
fnkc-fmba.ru	7	406	4864	complete
stomdevice.ru	9	231	2908	complete
zub-m.ru	10	163	620	complete
dentol.ru	10	165	3300	complete
yamed.ru	10	184	1214	complete
medsi.ru	10	1461	214043	complete
doct.ru	10	442	3600	complete
orgpage.ru	8	1080	194375	complete
paradent.ru	4	39	1559	complete
happydents.ru	10	26	238	complete
stom1.ru	10	152	10778	complete
22clinic.ru	10	149	383	complete
euro-dent.ru	10	253	652	complete
medcentr.biz	10	214	832	complete
like.doctor	2	154	1497	complete
zub.clinic	2	46	707	complete
smile-at-once.ru	4	216	26361	complete
stomatologi-msk.ru	3	8	55	complete
intelmedic.ru	8	28	444	complete
zubza.ru	3	86	237	complete
dentospas.ru	6	76	186	complete
vsevrachizdes.ru	6	270	4636	complete
norddental.ru	7	27	341	complete
familydoctor.ru	10	680	4700	complete
TopDent.ru	10	323	5950	complete
implant-expert.ru	6	59	141	complete
BabyBlog.ru	10	6306	648210	complete
MyDentist.ru	8	162	31884	complete
zapisatsya.ru	5	148	1522	complete
sprosivracha.com	4	369	19620	complete
klinikarassvet.ru	4	147	1278	complete
6750000.ru	10	117	1194	complete
shop-dent.ru	6	283	1476	complete
stomanshop.ru	6	21	81	complete
stomatologia-ilatan.ru	7	171	3402	complete
ADNclinic.ru	5	69	290	complete
stomatologiivse.ru	1	31	56	complete
DentaLain.ru	10	16	47	complete
zubov-implantaciya.ru	1	286	451	complete
ludent.ru	10	138	2247	complete
belgraviadent.ru	5	139	4339	complete
meds.ru	10	440	401657	complete
drclinics.ru	7	234	4457	complete
clinica-opora.ru	2	80	21392	complete
aktivstom.ru	10	45	617	complete
akademstom.ru	8	47	444	complete
samson-denta.ru	3	28	171	complete
alibus-dent.ru	5	13	47	complete
ddmedic.ru	6	61	1244	complete
geleodent.ru	10	40	77	complete
spravka.city	6	276	4516	complete
DentConsult.ru	8	268	3859	complete
mnogozubov.ru	7	278	4713	complete
alfascan3d.ru	2	4	74	complete
dentoland.com	3	123	3713	complete
spravka.ru	10	208	3312	complete
ultrasmile.ru	10	147	1593	complete
picasso-diagnostic.ru	10	214	1877	complete
seline.ru	10	122	674	complete
osnimke.ru	2	62	1183	complete
expert-stom.ru	10	32	78	complete
OnClinic.ru	10	725	32543	complete
family-dental.ru	7	84	202	complete
dcenergo.ru	9	374	3025	complete
dr-martin.ru	10	178	1501	complete
crocodent.ru	2	34	128	complete
zubrenok.ru	10	104	376	complete
martinka.ru	10	115	369	complete
LiderStom.ru	10	183	643	complete
dentalroott.ru	6	262	35910	complete
mamadeti.ru	10	1032	23042	complete
Naudent.ru	7	61	133	complete
TopSmile.ru	6	23	68	complete
kuponator.ru	10	1293	245468	complete
slclinic.ru	4	465	769	complete
implantprofi.ru	5	57	244	complete
vitadentmsk.ru	1	12	30	complete
CreateSmile.ru	5	181	2340	complete
totadres.ru	1	63	169	complete
rfadres.ru	3	36	97	complete
bigspr.ru	3	143	311708	complete
jsprav.ru	6	435	387597	complete
ktogdeest.com	5	168	382753	complete
стоматологиимосквы.рф	5	187	1360	complete
MoyaSpravka.ru	6	1488	9511	complete
beststom.ru	9	11	91	complete
lumident24.ru	0	29	798	complete
sc-dantist.ru	7	96	1218	complete
stmonalisa.ru	4	47	173	complete
spravker.ru	9	1229	639376	complete
spravka7.ru	3	138	622419	complete
kruglie-sutki.ru	10	323	840	complete
plan1.ru	10	521	3512	complete
4geo.ru	10	3736	598005	complete
spravochnika.ru	4	47	1325	complete
spravinform.ru	8	89	155	complete
SpravkaRu.info	6	92	1753	complete
kitabi.ru	5	230	621140	complete
ot-boli.ru	6	88	317	complete
mskmed.info	9	72	54427	complete
gdevrach.com	6	8	48	complete
minimum-price.ru	10	1277	18884	complete
a-medik.su	7	146	522	complete
dmaps.ru	6	71	251	complete
tilbagevise.ru	10	349	1442	complete
spr.ru	10	4937	995044	complete
bizly.ru	5	321	315185	complete
mosclinic.ru	10	736	67230	complete
ruborg.ru	2	100	466	complete
infodoctor.ru	10	711	10853	complete
103.рф	10	0	0	complete
back-in-ussr.com	9	780	31583	complete
ykt.ru	10	9757	10961616	complete
tvigle.ru	10	3553	58580	complete
polzam.ru	5	130	562	complete
more.tv	8	2080	969141	complete
megogo.ru	9	930	45269	complete
filmz.ru	10	3456	325215	complete
litmir.me	6	3421	102894	complete
bookscafe.net	7	780	458571	complete
lib.ru	10	23114	3575032	complete
ivi.tv	5	2124	170019	complete
massolit.top	0	66	66851	complete
mir-knig.com	0	129	1375	complete
moreskazok.ru	9	99	6948	complete
atanor.media	4	28	71	complete
yapokupayu.ru	10	1104	18092	complete
iknigi.net	7	1362	23303	complete
deti-online.com	8	1919	68587	complete
slavclub.ru	10	118	1589	complete
avidreaders.ru	6	1108	8908	complete
mishka-knizhka.ru	2	1137	11192	complete
frigato.ru	2	192	4431	complete
TopSpiski.com	4	186	180454	complete
nukadeti.ru	3	349	42952	complete
miloliza.com	10	152	1078	complete
librebook.me	3	817	1513265	complete
mamontenok-online.ru	3	273	3178	complete
dobrye-skazki.ru	3	39	112	complete
mp3tales.info	8	543	21182	complete
ozornik.net	4	171	2066	complete
posmotre.li	5	802	13840	complete
chitaem-vmeste.ru	10	379	314880	complete
fantlab.ru	10	3419	871766	complete
great-country.ru	10	451	21635	complete
soyuz.ru	10	1644	48557	complete
wikifur.com	10	2611	448466	complete
larec-skazok.ru	5	56	313	complete
inforazum.ru	9	39	133	complete
battle.net	10	15745	16066010	complete
igromania.ru	10	3883	855668	complete
dtf.ru	10	3666	173267	complete
CyberSport.ru	10	2682	600801	complete
kanobu.ru	10	3725	167749	complete
playground.ru	10	5214	9000156	complete
worldofwarcraft.com	10	22599	11244310	complete
byrutor.org	1	105	10929	complete
igromagnit.net	3	88	556	complete
moreigr.com	0	73	841	complete
mega-mult.ru	10	438	4023	complete
fanfics.me	6	928	619545	complete
kinoafisha.info	10	1173	118348	complete
hnoph.top	1	128	1569	complete
kinonews.ru	10	2244	184513	complete
kadikama.ru	4	182	7195	complete
lord-film.cc	0	27	111	complete
multfilms.online	1	69	991	complete
filmive-hd.net	1	1052	53887	complete
disney.ru	10	2736	678132	complete
ruserialy.net	2	360	3861	complete
liveam.tv	6	584	9320	complete
gorzdrav.org	10	782	18719	complete
kinosezon.net	0	114	21825	complete
sunnycircle.ru	10	22	667	complete
rserialy.net	0	6	389	complete
russkii-serial.net	1	62	2705	complete
lordfilm-hd.net	0	58	82083	complete
META.ltd	3	12	127	complete
muztron.com	1	140	3379	complete
detskie-pesni.ru	0	158	53910	complete
rserial.net	1	52	1837	complete
hotplayer.ru	2	417	4050	complete
film.ru	10	4036	1505462	complete
livelib.ru	10	7130	797442	complete
cinetexts.ru	2	16	53	complete
lordfilm.so	0	918	54892	complete
melnitsa.com	10	243	2460	complete
deti123.ru	3	229	1476	complete
qna.center	6	397	1988	complete
pravda.ru	10	13327	1288131	complete
AfterShock.news	5	2368	2518677	complete
yaplakal.com	10	17910	2652094	complete
newsmuz.com	7	1399	132352	complete
universe-tss.su	7	810	29839	complete
wiki2.info	0	111	3184	complete
sv-scena.ru	8	143	1214	complete
langalex.com	5	29	131	complete
warhead.su	4	954	58609	complete
potolkynedorogo.ru	4	11	101	complete
evita-potolki.ru	2	1006	24807	complete
Potolok.net	7	27	582	complete
potolochek.su	9	3	57	complete
mahaon124.ru	5	13	48	complete
100potolkov.ru	9	44	101	complete
arnuvo.pro	2	3	4	complete
ppk-potolki.ru	4	70	134	complete
TattooStation.ru	4	8	30	complete
odintattoo.ru	8	7	14	complete
tattoox.ru	10	83	523	complete
pix-feed.com	3	342	5910	complete
ilovetattoos.ru	2	1	1	complete
miamitats.com	5	24	73	complete
inkppl.com	4	279	3469	complete
everink.ru	0	3	4	complete
maze.tattoo	2	14	112	complete
stomos.ru	10	104	586	complete
stomed.ru	10	600	4200	complete
32Dent.ru	10	498	6753	complete
euro-stom.ru	6	51	677	complete
centerstom.com	7	56	99	complete
vaodent.ru	10	538	1170	complete
gdenta.ru	7	40	107	complete
ortodontcomplex.ru	2	399	2711	complete
lpsdenta.ru	10	30	63	complete
ldent.com	10	35	149	complete
лечимзубы.москва	2	3	7	complete
Korrektsiya-zreniya.ru	1	94	726	complete
visus-novus.ru	10	104	338	complete
визион.рф	10	37	453	complete
Belikova.ru	6	378	7510	complete
samag.ru	10	1383	236372	complete
PythonWorld.ru	8	372	10819	complete
tproger.ru	8	1500	101186	complete
medium.com	10	653531	290553086	complete
python-scripts.com	4	722	5600	complete
proglib.io	4	651	32464	complete
ilnurgi1.ru	7	15	100	complete
tirinox.ru	9	16	26	complete
docs-python.ru	0	28	33	complete
8host.com	10	180	2309	complete
codecamp.ru	5	38	200	complete
hexlet.io	6	560	6160	complete
mipt.ru	10	7256	607738	complete
pythononline.ru	0	10	17	complete
machinelearningmastery.ru	1	38	127	complete
nuancesprog.ru	2	73	3027	complete
riptutorial.com	2	1252	684281	complete
bugaga.ru	10	3261	1711576	complete
pcsecrets.ru	10	371	2022	complete
teenslang.su	10	904	245391	complete
cyclowiki.org	10	3706	300444	complete
KtoNaNovenkogo.ru	10	1619	23594	complete
TexTerra.ru	10	2101	314410	complete
sonikelf.ru	10	1099	47956	complete
ocomp.info	4	884	27073	complete
artlebedev.ru	10	8930	5260953	complete
wiktionary.org	10	2020	95891	complete
azbyka.ru	10	7663	3856501	complete
mel.fm	5	3869	904258	complete
multyshi.ru	5	6	8	complete
souzmult.ru	10	490	88212	complete
multfest.ru	10	402	711762	complete
chitalnya.ru	10	2643	120382	complete
v7u.org	10	123	1137	complete
hodor.lol	4	387	1981	complete
steamcommunity.com	10	82268	311820818	complete
dotabuff.com	8	2925	563617	complete
vimeworld.ru	7	129	28017	complete
PromoDJ.com	10	12956	1612294	complete
fotostrana.ru	10	3042	323549	complete
last.fm	10	78243	81989420	complete
muzebra.me	0	185	10929	complete
ecigtalk.ru	10	1775	69687	complete
24review.ru	4	80	2144	complete
SaleTur.ru	10	990	897196	complete
1000turov.ru	10	601	4195	complete
TopHotels.ru	10	3127	3558606	complete
turskidki.ru	10	1546	193716	complete
tez-tour.com	10	2476	352107	complete
otdyhateli.com	4	90	265	complete
catwar.su	9	50	25664	complete
ipleer.com	9	222	5674	complete
5music.me	1	97	46992	complete
muzaza.ru	2	476	152983	complete
mp3ex.xyz	0	424	15102	complete
ka4ka.mobi	0	5	54	complete
leagueofgraphs.com	7	752	168525	complete
egyptpro.ru	5	14	26	complete
kiteteam.ru	10	94	1304	complete
travelata.ru	9	865	176872	complete
safaga.ru	10	19	67	complete
bgoperator.ru	10	1741	1229984	complete
booking.com	10	519720	344504030	complete
mp3baza.me	0	280	12645	complete
OnlineTours.ru	10	1501	77041	complete
rt.ru	10	10755	7169052	complete
glaz-tv.online	2	114	757	complete
tvzavr.ru	10	1460	45898	complete
federal.tv	3	42	585	complete
glaz-ok.online	0	42	91	complete
glaz.tv	9	3404	125694	complete
kartafx.ru	4	42	63	complete
rossaprimavera.ru	4	3862	1285797	complete
rzev.ru	10	140	1351	complete
may9.ru	10	5455	10283589	complete
rubaltic.ru	10	2089	2507334	complete
kartarf.ru	4	149	1918	complete
mapdata.ru	6	243	34678	complete
kodifikant.ru	8	247	3041	complete
frf.su	10	2	4	complete
clip-share.net	2	244	4640	complete
roskarta.net	6	54	130	complete
RusMap.net	6	218	1777	complete
russiakarty.ru	3	17	24	complete
semyaivera.ru	9	327	59526	complete
7fa.ru	6	121	931380	complete
eva.ru	10	5455	454070	complete
mamba.ru	10	2314	344408	complete
baku.ru	10	818	100178	complete
FarGate.ru	10	275	1024	complete
fifa08.ru	10	7	1867	complete
trk-tura.ru	8	145	187350	complete
soczashhita.ru	2	37	151	complete
fargat.ru	0	0	0	complete
kuraj-bambey.ru	10	345	4473	complete
eurasica.ru	10	667	58389	complete
kurganoblduma.ru	8	123	1568212	complete
rp5.am	5	53	4827	complete
62live.ru	10	301	6188	complete
кооп48.рф	3	15	6999	complete
kooop39.ru	6	16	343	complete
koop41.ru	10	23	144	complete
versuri.ro	5	724	11906	complete
metallurgu.ru	8	55	143	complete
metal-archive.ru	6	401	2736	complete
rusknife.com	10	663	27691	complete
metalloy.ru	2	90	317	complete
versmet.ru	10	47	648	complete
metall-metalloprokat.ru	4	5	12	complete
metallsam.ru	9	26	40	complete
stalimetal.ru	0	31	6262	complete
metall-ps.ru	10	26	111	complete
lazermetal.ru	2	21	28	complete
dametall.ru	1	-1	-1	complete
meshok.net	10	3848	610050	complete
vt-metall.ru	6	81	198	complete
metall-tm.ru	6	3	3	complete
metalliko116.ru	1	1	1	complete
tar-metall.ru	0	-1	-1	complete
metall-i-ka.ru	7	35	1699	complete
DokMetall.ru	0	25	43	complete
vi-stal.ru	10	18	46	complete
oz-metalla.ru	4	1	2385	complete
zismetall.ru	2	2	2	complete
tpu.ru	10	885	14616	complete
museumrza.ru	10	96	2463	complete
elec.ru	10	1830	888521	complete
electric-220.ru	9	193	1075	complete
sudact.ru	8	4233	478435	complete
pomegerim.ru	3	22	91	complete
ElectricalSchool.info	10	993	23674	complete
контрользнаний.рф	5	98	787	complete
aznaetelivy.ru	10	318	8895	complete
Elektrik-a.su	4	115	1892	complete
Spadilo.ru	9	202	4217	complete
metaschool.ru	10	506	255937	complete
asutpp.ru	10	262	3485	complete
letovo.online	1	95	2170	complete
restoran.ru	10	1415	10881	complete
smileeyes.ru	5	59	2972	complete
doktorlaser.ru	8	105	218	complete
frazy.su	9	428	1572	complete
travelask.ru	7	1926	77945	complete
disgustingmen.com	7	1251	15654	complete
litsovet.ru	10	1339	28234	complete
schooltests.ru	7	21	195	complete
KudaGo.com	8	3289	407010	complete
formaxfun.com	3	20	60	complete
wiki2.net	0	191	63583	complete
videouroki.net	10	3372	17381886	complete
multiurok.ru	6	2911	1473886	complete
gdz.red	0	122	157882	complete
tvkinoradio.ru	9	829	117589	complete
rbook.me	3	146	1012	complete
sanstv.ru	9	418	21629	complete
Italy4.me	8	603	2992	complete
pravlife.org	8	1128	106582	complete
dropi.ru	8	319	1755	complete
iq2u.ru	6	464	14715	complete
o-eda-dostavka.ru	2	34	3774	complete
kinorium.com	6	119	9396	complete
cattur.ru	5	113	620	complete
gamer-info.com	10	1888	79943	complete
PlayMap.ru	8	200	61923	complete
wotblitz.ru	8	297	825058	complete
ustaliy.ru	4	361	14196	complete
KinoMania.ru	10	2070	167025	complete
konovalov-eye-center.ru	10	311	3323	complete
wiki-org.ru	4	467	3407	complete
booksread.info	0	0	0	complete
rugames.org	0	0	0	complete
skills4u.ru	2	175	639	complete
duhmaga.ru	2	181	2774	complete
pevuz.ru	7	6	15	complete
touristam.com	2	185	764	complete
corsairs-harbour.com	10	11	37	complete
utorrentgames.pro	0	0	0	complete
wiki-rza.ru	6	6	12	complete
allcafe.ru	10	1037	203682	complete
Lifehacker.ru	10	10481	1068684	complete
piphia.ru	2	65	457	complete
libking.ru	2	883	6942	complete
corsairs-harbour.ru	10	802	67644	complete
pirate-islands.com	4	37	4320	complete
ToolProkat43.ru	0	4	58	complete
BroDude.ru	8	1236	1054676	complete
glaz-center.com	4	35	79	complete
дословно.рф	1	135	663	complete
ageiron.ru	7	88	1044	complete
cable.ru	10	1091	354989	complete
delivery-club.ru	10	1732	693867	complete
kinoart.ru	10	1743	37521	complete
operaciya.org	3	9	77	complete
mensby.com	8	326	2013	complete
mir-knigi.info	0	61	8752	complete
expertitaly.ru	6	56	250	complete
info-pirat.ru	8	1	1	complete
OFaze.ru	1	29	41	complete
multoigri.ru	5	1624	89885	complete
ophthalmocenter.ru	3	39	160	complete
vse-shutochki.ru	6	303	7685	complete
lumos22.com	3	148	718	complete
toitaly.info	3	22	39	complete
catorrent.org	4	175	493	complete
libbox.club	5	65	619	complete
eyesmile.ru	5	2	2	complete
azialand.ru	8	199	595	complete
knigi-for.me	0	38	63	complete
MyChinaExpert.ru	4	131	322	complete
masterokblog.ru	2	141	11755	complete
pirates-life.ru	10	728	3063	complete
wikireading.ru	5	140	2576	complete
elektronchic.ru	5	59	429	complete
analizfamilii.ru	10	837	197082	complete
restaurantguru.com	10	6591	5539725	complete
mult.tv	3	150	166054	complete
проверьзрение.рф	5	31	421	complete
dveimperii.ru	10	132	4380	complete
KnowHistory.ru	10	150	745	complete
tepler.ru	5	42	122	complete
historic.ru	10	3497	70366	complete
znachenie-imeni-familii.ru	2	39	1804	complete
chinagramota.ru	6	130	389	complete
vseigru.net	5	900	48807	complete
proglaza.net	2	115	2173	complete
self-creation.info	6	31	63	complete
audioliba.com	0	73	840	complete
miroworld.ru	4	69	236	complete
italyme.ru	4	26	60	complete
author.today	5	976	881534	complete
domkino.tv	10	949	80118	complete
smile-correction.com	4	3	63	complete
narod.ru	10	104125	57893362	complete
sainte-anastasie.org	1	11	20	complete
ArchitectureGuru.ru	2	81	351	complete
theplacement.ru	6	62	249	complete
onlinetestpad.com	9	3338	662797	complete
stihistat.com	10	300	1386	complete
eda.yandex	5	1161	123529	complete
igroutka.ru	4	1157	66674	complete
eyeclinics.ru	6	12	19	complete
symbolarium.ru	10	357	1738	complete
wikiway.com	10	577	7175	complete
planetofhotels.com	7	2595	44856	complete
cont.ws	6	6892	15576052	complete
ElektroKlub-nn.ru	0	7	29	complete
RosGenea.ru	10	569	21781	complete
localway.ru	8	314	2090	complete
mtbank.by	10	889	156548	complete
bookshake.net	1	218	1361	complete
gufo.me	6	3966	159927	complete
anashina.com	9	758	7227	complete
postnauka.ru	9	3904	86492	complete
TestEdu.ru	8	404	20739	complete
a-a-ah.ru	10	870	260743	complete
resfeber.ru	3	158	612	complete
nmtkursk.ru	2	26	3786	complete
e-news.su	6	1665	67522	complete
elektrik-sam.ru	0	12	306	complete
linzy.ru	10	299	1123	complete
2queens.ru	9	297	1975	complete
magazeta.com	10	1014	33595	complete
perunica.ru	10	1472	25520	complete
pirates.travel	4	232	8079	complete
StoneForest.ru	7	312	4753	complete
agk-sport.ru	2	30	126	complete
mntk.ru	10	827	9975	complete
MyBook.ru	10	3118	2941126	complete
puteshestvovat.com	4	52	204	complete
factik.ru	9	155	493	complete
infourok.ru	8	8680	1947578	complete
realeyes.ru	10	37	75	complete
greednews.su	2	453	3070	complete
topliba.com	2	93	2958	complete
ostrovok.ru	10	6555	2163999	complete
arzamas.academy	6	5168	75117	complete
\.


--
-- Data for Name: main_handledxml; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_handledxml (request, xml, status) FROM stdin;
\.


--
-- Data for Name: main_order; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_order (id, request_id, user_id, order_id) FROM stdin;
259	213	31	30
260	214	31	31
261	215	31	32
262	216	31	32
263	217	31	33
264	218	31	33
265	219	31	33
266	220	31	33
\.


--
-- Data for Name: main_orderstatus; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_orderstatus (order_id, status, progress, user_id, ordered_keywords_amount, user_order_id) FROM stdin;
30	1	100	31	1	1
31	1	100	31	1	2
32	1	100	31	2	3
33	1	100	31	4	4
\.


--
-- Data for Name: main_payload; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_payload (key, balance) FROM stdin;
4a02e0c1e8a93c66e09970186a351852	98
\.


--
-- Data for Name: main_request; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_request (request_id, request_text, site_age_concurency, site_stem_concurency, site_volume_concurency, site_backlinks_concurency, site_total_concurency, direct_upscale, status, site_direct_concurency, site_seo_concurency) FROM stdin;
213	коррекция зрения	91	98	99	89	128	35	ready	100	93
214	китайская стена	79	97	99	66	83	0.6	ready	1	83
215	пизанская башня	77	100	96	76	85	0.6	ready	1	85
216	победы курск	88	92	64	80	99	14.8	ready	42	85
217	пираты	93	95	91	95	93	0.6	ready	1	93
218	корсары	85	100	78	82	89	1.8	ready	5	88
220	лангорьеры	90	43	78	94	75	0.6	ready	1	75
219	буканьеры	90	96	93	86	91	0	ready	0	91
\.


--
-- Data for Name: main_requestqueue; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_requestqueue (request_text) FROM stdin;
\.


--
-- Data for Name: main_ticket; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_ticket (ticket_id, author_id, status, opened, closed, user_ticket_id) FROM stdin;
2	16	closed	2021-02-10 14:49:02.227456+03	2021-02-10 15:31:42.187414+03	1
3	17	closed	2021-02-10 15:00:46.446159+03	2021-02-10 15:31:46.696401+03	1
1	16	closed	2021-02-10 14:46:26.159766+03	2021-02-10 15:31:50.042754+03	1
4	17	closed	2021-02-10 15:31:53.403044+03	2021-02-10 15:31:55.27382+03	1
5	17	closed	2021-02-10 15:32:14.156316+03	2021-02-10 15:32:23.851593+03	1
6	17	closed	2021-02-10 15:35:16.51953+03	2021-02-10 15:35:18.837984+03	1
25	27	closed	2021-02-13 17:40:48.967941+03	2021-02-13 18:06:49.390211+03	2
24	27	closed	2021-02-13 17:40:37.36745+03	2021-02-13 18:06:53.016901+03	1
23	25	closed	2021-02-13 15:59:49.989547+03	2021-02-13 18:06:54.911262+03	2
22	25	closed	2021-02-13 15:59:30.232118+03	2021-02-13 18:06:56.778294+03	1
21	24	closed	2021-02-13 15:57:22.103584+03	2021-02-13 18:06:58.492662+03	7
20	24	closed	2021-02-13 15:57:12.809114+03	2021-02-13 18:06:59.86173+03	6
19	24	closed	2021-02-13 15:56:54.19193+03	2021-02-13 18:07:01.35407+03	5
18	24	closed	2021-02-13 15:55:23.114582+03	2021-02-13 18:07:02.802567+03	4
17	24	closed	2021-02-13 15:55:10.18545+03	2021-02-13 18:07:03.502049+03	3
16	24	closed	2021-02-13 15:32:42.458486+03	2021-02-15 14:34:29.740061+03	2
26	27	closed	2021-02-13 18:07:36.649312+03	2021-02-15 14:34:34.010242+03	3
15	24	closed	2021-02-13 15:32:30.381114+03	2021-02-15 14:34:38.660846+03	1
14	23	closed	2021-02-13 15:30:54.148357+03	2021-02-15 14:34:40.665929+03	2
13	23	closed	2021-02-13 15:30:20.602735+03	2021-02-15 14:34:41.859687+03	1
12	23	closed	2021-02-13 15:29:42.366424+03	2021-02-15 14:34:42.813034+03	1
11	23	closed	2021-02-13 15:15:37.827762+03	2021-02-15 14:34:43.718909+03	1
10	22	closed	2021-02-12 11:55:09.439036+03	2021-02-15 14:34:45.569243+03	1
9	22	closed	2021-02-12 11:52:05.455684+03	2021-02-15 14:34:46.661686+03	1
8	18	closed	2021-02-10 15:40:37.476907+03	2021-02-15 14:34:47.482298+03	1
7	18	closed	2021-02-10 15:40:13.289928+03	2021-02-15 14:34:48.374505+03	1
29	28	closed	2021-02-15 15:09:42.278304+03	2021-02-15 15:11:36.135951+03	2
27	17	closed	2021-02-15 14:34:52.954009+03	2021-02-15 15:12:03.472415+03	2
28	28	closed	2021-02-15 15:09:27.109184+03	2021-02-15 15:12:31.327673+03	1
30	31	closed	2021-02-16 13:28:56.554848+03	2021-02-16 13:30:17.515059+03	1
\.


--
-- Data for Name: main_ticketpost; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_ticketpost (ticket_post_id, ticket_id, ticket_post_author_id, ticket_post_text, ticket_post_order) FROM stdin;
25	11	23	rwerwerwe	0
26	12	23	sadasafsa	0
27	13	23	gasgaga	0
28	14	23	reyeryerye	0
29	15	24	fsdfsd	0
30	15	24	wewetwe	0
31	16	24	rtkreterotkero	0
32	2	24	rggggregre	0
33	2	24	rgregregeerheher	0
34	2	24	dsadasdas	0
35	16	24	grfggewgre	0
36	16	24	65634634\r\n	0
37	16	24	qetrewtwe	0
38	16	24	123	0
39	15	24	rge	0
40	20	24	fksdkgspdkg[sd	0
41	20	24	kgopgo	0
42	21	24	ltp43[tl43	0
43	22	25	saalfmlsamfla;s	0
44	22	25	sdgdsmg;lkweopgwegwe	0
45	23	25	sdlgmsdpogwsd	0
46	24	27	кпкупук	0
47	24	27	апав	0
48	25	27	уауцацуацу	0
49	25	27	gfdfgd	0
50	26	27	dsgsd	0
51	25	27	gfdg	0
52	16	17	5454	0
53	28	28	Тикет готов	0
54	28	28	второй пост в тикет	0
55	29	28	И еще один тикет	0
56	29	28	со вторым постом	0
57	29	28	и третьим	0
58	29	17	ответ	0
59	27	17	ответ	0
60	28	17	ааывыв	0
61	29	28	treter	0
62	30	31	sfsdfsd	0
\.


--
-- Data for Name: main_userdata; Type: TABLE DATA; Schema: concurent_site; Owner: postgres
--

COPY concurent_site.main_userdata (user_id, balance, ordered_keywords, orders_amount) FROM stdin;
16	44	6	3
18	43	7	3
19	50	0	0
22	48	2	1
21	20	30	16
23	42	8	2
24	50	0	0
25	45	5	2
26	31	19	3
17	47	3	2
28	36	14	11
29	50	0	0
30	50	0	0
27	32	18	7
31	36	14	8
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_permission_id_seq', 68, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_user_id_seq', 31, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.django_content_type_id_seq', 17, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.django_migrations_id_seq', 50, true);


--
-- Name: main_order_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_order_id_seq', 266, true);


--
-- Name: main_orderstatus_order_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_orderstatus_order_id_seq', 33, true);


--
-- Name: main_request_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_request_id_seq', 1161, true);


--
-- Name: main_request_request_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_request_request_id_seq', 220, true);


--
-- Name: main_ticket_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_ticket_id_seq', 63, true);


--
-- Name: main_ticket_ticket_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_ticket_ticket_id_seq', 30, true);


--
-- Name: main_ticketpost_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_ticketpost_id_seq', 53, true);


--
-- Name: main_ticketpost_ticket_post_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_ticketpost_ticket_post_id_seq', 62, true);


--
-- Name: main_userdata_id_seq; Type: SEQUENCE SET; Schema: concurent_site; Owner: postgres
--

SELECT pg_catalog.setval('concurent_site.main_userdata_id_seq', 11, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: main_domain main_domain_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_domain
    ADD CONSTRAINT main_domain_pkey PRIMARY KEY (name);


--
-- Name: main_handledxml main_handledxml_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_handledxml
    ADD CONSTRAINT main_handledxml_pkey PRIMARY KEY (request);


--
-- Name: main_order main_order_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_order
    ADD CONSTRAINT main_order_pkey PRIMARY KEY (id);


--
-- Name: main_orderstatus main_orderstatus_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_orderstatus
    ADD CONSTRAINT main_orderstatus_pkey PRIMARY KEY (order_id);


--
-- Name: main_payload main_payload_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_payload
    ADD CONSTRAINT main_payload_pkey PRIMARY KEY (key);


--
-- Name: main_request main_request_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_request
    ADD CONSTRAINT main_request_pkey PRIMARY KEY (request_id);


--
-- Name: main_requestqueue main_requestqueue_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_requestqueue
    ADD CONSTRAINT main_requestqueue_pkey PRIMARY KEY (request_text);


--
-- Name: main_ticket main_ticket_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticket
    ADD CONSTRAINT main_ticket_pkey PRIMARY KEY (ticket_id);


--
-- Name: main_ticketpost main_ticketpost_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticketpost
    ADD CONSTRAINT main_ticketpost_pkey PRIMARY KEY (ticket_post_id);


--
-- Name: main_userdata main_userdata_pkey; Type: CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_userdata
    ADD CONSTRAINT main_userdata_pkey PRIMARY KEY (user_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON concurent_site.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON concurent_site.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON concurent_site.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON concurent_site.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_user_groups_group_id_97559544 ON concurent_site.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON concurent_site.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON concurent_site.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON concurent_site.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX auth_user_username_6821ab7c_like ON concurent_site.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON concurent_site.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON concurent_site.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON concurent_site.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON concurent_site.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: main_domain_name_3fb3d42c_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_domain_name_3fb3d42c_like ON concurent_site.main_domain USING btree (name varchar_pattern_ops);


--
-- Name: main_handledxml_request_a38ea638_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_handledxml_request_a38ea638_like ON concurent_site.main_handledxml USING btree (request varchar_pattern_ops);


--
-- Name: main_order_order_id_id_5eafe42e; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_order_order_id_id_5eafe42e ON concurent_site.main_order USING btree (order_id);


--
-- Name: main_order_request_id_id_fdb758da; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_order_request_id_id_fdb758da ON concurent_site.main_order USING btree (request_id);


--
-- Name: main_order_user_id_id_8eecd7ba; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_order_user_id_id_8eecd7ba ON concurent_site.main_order USING btree (user_id);


--
-- Name: main_orderstatus_user_id_id_8107d809; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_orderstatus_user_id_id_8107d809 ON concurent_site.main_orderstatus USING btree (user_id);


--
-- Name: main_payload_key_1d8027f2_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_payload_key_1d8027f2_like ON concurent_site.main_payload USING btree (key varchar_pattern_ops);


--
-- Name: main_requestqueue_request_6ad3f1e4_like; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_requestqueue_request_6ad3f1e4_like ON concurent_site.main_requestqueue USING btree (request_text varchar_pattern_ops);


--
-- Name: main_ticket_author_id_306581ec; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_ticket_author_id_306581ec ON concurent_site.main_ticket USING btree (author_id);


--
-- Name: main_ticketpost_ticked_id_id_ed5f9717; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_ticketpost_ticked_id_id_ed5f9717 ON concurent_site.main_ticketpost USING btree (ticket_id);


--
-- Name: main_ticketpost_ticket_post_author_id_bb658c5d; Type: INDEX; Schema: concurent_site; Owner: postgres
--

CREATE INDEX main_ticketpost_ticket_post_author_id_bb658c5d ON concurent_site.main_ticketpost USING btree (ticket_post_author_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES concurent_site.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES concurent_site.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES concurent_site.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES concurent_site.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES concurent_site.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES concurent_site.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_order main_order_order_id_bca29b9b_fk; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_order
    ADD CONSTRAINT main_order_order_id_bca29b9b_fk FOREIGN KEY (order_id) REFERENCES concurent_site.main_orderstatus(order_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_order main_order_request_id_733de175_fk; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_order
    ADD CONSTRAINT main_order_request_id_733de175_fk FOREIGN KEY (request_id) REFERENCES concurent_site.main_request(request_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_order main_order_user_id_f3a58861_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_order
    ADD CONSTRAINT main_order_user_id_f3a58861_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_orderstatus main_orderstatus_user_id_839aafe1_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_orderstatus
    ADD CONSTRAINT main_orderstatus_user_id_839aafe1_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_ticket main_ticket_author_id_306581ec_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticket
    ADD CONSTRAINT main_ticket_author_id_306581ec_fk_auth_user_id FOREIGN KEY (author_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_ticketpost main_ticketpost_ticket_id_a4cc6d17_fk; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticketpost
    ADD CONSTRAINT main_ticketpost_ticket_id_a4cc6d17_fk FOREIGN KEY (ticket_id) REFERENCES concurent_site.main_ticket(ticket_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_ticketpost main_ticketpost_ticket_post_author_id_bb658c5d_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_ticketpost
    ADD CONSTRAINT main_ticketpost_ticket_post_author_id_bb658c5d_fk_auth_user_id FOREIGN KEY (ticket_post_author_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_userdata main_userdata_user_id_7ff39629_fk_auth_user_id; Type: FK CONSTRAINT; Schema: concurent_site; Owner: postgres
--

ALTER TABLE ONLY concurent_site.main_userdata
    ADD CONSTRAINT main_userdata_user_id_7ff39629_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES concurent_site.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

