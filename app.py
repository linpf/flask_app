import csv
import datetime
from datetime import date

import pygal
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_caching import Cache

hr_short_name = {}
hr_region = {}

can_folder_path = "data/CovidTimelineCanada/data/can/"
pt_folder_path = "data/CovidTimelineCanada/data/pt/"
hr_folder_path = "data/CovidTimelineCanada/data/hr/"

def read_hr_id2name_maping_table():

    with open("data/CovidTimelineCanada/geo/hr.csv", 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            hr_short_name[row_data["hruid"]] = row_data["name_short"]
            hr_region[row_data["hruid"]] = row_data["region"]


read_hr_id2name_maping_table()
app = Flask(__name__)
Bootstrap5(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/')
@app.route('/home')
@app.route('/home/<start_date>')
@cache.cached(timeout=3600)
def home(start_date=None):

    chart2 = can_weekly_chart_from_files(pygal.Bar,
                                         [("deaths",
                                           False),
                                          ("hospitalizations", True), ],
                                         "",
                                         start_date)

    chart4 = can_weekly_chart_from_files(pygal.Bar,
                                         [
                                             ("hospitalizations", True),
                                             ("cases", False)],
                                         "", start_date)

    chart1 = can_weekly_chart_from_files(pygal.StackedBar,
                                         [("deaths", False), ],
                                         "", start_date)

    # chart4 = can_weekly_chart_from_files(pygal.Bar,
    #                                      [
    #                                          ("icu", True), ],
    #                                      "", start_date)

    chart5 = can_charts([pygal.Bar,],True,
                                 ["icu"],
                                 False,
                                 start_date,
                                 legend_at_bottom=True)[0]



    chart3 = can_charts([pygal.Bar,],True,
                                 ["hospitalizations"],
                                 False,
                                 start_date,
                                 legend_at_bottom=True)[0]


    # chart11 = can_pts_summary_chart(
    #     pygal.HorizontalStackedBar,
    #     reversed([("cases", False), ("deaths", False)]),
    #     legend_at_bottom=True)


    chart6 = can_weekly_chart_from_files(pygal.Bar,
                                         [("cases",
                                           False),
                                          ("tests_completed",
                                           False)],
                                         "", start_date, dots_size=1)

    chart7 = can_weekly_chart_from_files(pygal.Line,
                                         [("vaccine_administration_dose_1", True),
                                             ("vaccine_administration_dose_2", True),
                                             ("vaccine_administration_dose_3", True),
                                             ("vaccine_administration_dose_4", True), ],
                                         "", start_date,)

    chart8 = can_weekly_chart_from_files(pygal.Line,
                                         [("vaccine_coverage_dose_1", True),
                                          ("vaccine_coverage_dose_2", True),
                                          ("vaccine_coverage_dose_3", True),
                                          ("vaccine_coverage_dose_4", True), ],
                                         "", start_date,)

    (chart9,) = can_charts([pygal.Line, ], True, [
        "deaths", "cases"], False, start_date, show_legend=True, legend_at_bottom=True)

    (chart10,) = can_charts([pygal.Line, ], True, [
        "deaths"], False, start_date, show_legend=True, legend_at_bottom=True)

    charts = [
        chart1,
        chart2,
        chart3,
        chart4,
        chart5,
        chart6,
        chart7,
        chart8,
        chart9,
        chart10]

    page_title = "Canada from " + start_date if start_date else "Canada "

    return render_template(
        'charts.html',
        charts=charts,
        page_title=page_title,
        updated_date=read_update_time(),
        start_date=start_date,
        attr="cases")


@app.route('/hrs_view')
@cache.cached(timeout=3600)
def hrs_view():

    chart2 = hrs_chart(
        "cases", sample_by_week=True,
        show_legend=False)

    chart1 = hrs_chart(
        "deaths",
        sample_by_week=True,
        show_legend=False)

    chart4 = hr_chart(
        pygal.HorizontalStackedBar,
        "cases",
        show_legend=False)

    chart3 = hr_chart(
        pygal.HorizontalStackedBar,
        "deaths",
        show_legend=False)

    chart6 = hr_chart(
        pygal.HorizontalStackedBar,
        "cases",
        legend_at_bottom=True, margin_bottom=0, show_x_labels=False)

    chart5 = hr_chart(
        pygal.HorizontalStackedBar,
        "deaths",
        legend_at_bottom=True, margin_bottom=0, show_x_labels=False)

    chart8 = hr_chart(
        pygal.Treemap,
        "cases",
        show_legend=False)

    chart7 = hr_chart(
        pygal.Treemap,
        "deaths",
        show_legend=False)

    charts = [chart1, chart2, chart7, chart8, chart5, chart6, chart3, chart4]

    return render_template(
        'charts.html',
        charts=charts,
        attr="cases",
        updated_date=read_update_time())


@app.route('/hr_attr_view/<region>/<sub_region_1>/<attr>/<start_date>')
@app.route('/hr_attr_view/<region>/<sub_region_1>/<attr>')
@cache.cached(timeout=3600)
def hr_attr_view(region, sub_region_1, attr, start_date=None):

    charts_set = hr_charts(region,
                           sub_region_1,
                           [pygal.Bar,
                            pygal.Treemap,
                            pygal.Pie],
                           False,
                           [attr],
                           True,
                           start_date) + hr_charts(region,
                                                   sub_region_1,
                                                   [pygal.Bar, pygal.Treemap, pygal.Pie],
                                                   False,
                                                   [attr],
                                                   False,
                                                   start_date)

    page_title = region + ", " + \
        hr_short_name.get(sub_region_1, sub_region_1) + " - " + attr.capitalize()

    return render_template(
        'charts.html',
        charts=charts_set,
        page_title=page_title,
        attr=attr,
        updated_date=read_update_time())


@app.route('/pt_attr_view/<region>/<attr>/<start_date>')
@app.route('/pt_attr_view/<region>/<attr>')
@cache.cached(timeout=3600)
def pt_attr_view(region, attr, start_date=None):
    if attr in ["cases", "deaths", "tests_completed"]:
        cumulated = False
    else:
        cumulated = True

    charts_set = pt_charts(region,
                           [pygal.Bar,
                            pygal.Treemap],
                           cumulated,
                           attr,
                           True,
                           start_date) + pt_charts(region,
                                                   [pygal.Bar,
                                                    pygal.Treemap],
                                                   cumulated,
                                                   attr,
                                                   False,
                                                   start_date)

    page_title = region + " - " + attr.upper()

    return render_template(
        'charts.html',
        charts=charts_set,
        attr=attr,
        start_date=start_date,
        page_title=page_title,
        updated_date=read_update_time())


@app.route('/pts_attr_view/<attr>/<start_date>')
@app.route('/pts_attr_view/<attr>/')
@app.route('/pts_attr_view/<attr>')
@cache.cached(timeout=3600)
def pts_attr_view(attr, start_date=None):
    if attr in ["cases", "deaths", "tests_completed"]:
        cumulated = False
    else:
        cumulated = True

    charts_set = pts_charts([pygal.StackedBar,
                             pygal.Treemap,
                             pygal.Pie],
                             cumulated,
                             attr,
                             True,
                             start_date) + pts_charts([pygal.StackedBar,
                                                      pygal.Treemap,
                                                      pygal.Pie],
                                                     cumulated,
                                                     attr,
                                                     False,
                                                     start_date)

    page_title = "Provinces/Territories - " + attr

    return render_template(
        'charts.html',
        charts=charts_set,
        page_title=page_title,
        updated_date=read_update_time(),
        start_date=start_date)


@app.route('/can_attr_view/<attr>')
@app.route('/can_attr_view/<attr>/<start_date>')
@cache.cached(timeout=3600)
def can_attr_view(attr, start_date=None):

    if attr in ["cases", "deaths", "tests_completed"]:
        cumulated = False
    else:
        cumulated = True

    if attr in ["icu", "hospitalizations"]:

        charts_set2 = pts_charts([pygal.StackedBar,
                                  pygal.Treemap,
                                  ],
                                 cumulated,
                                 attr,
                                 True,
                                 start_date,
                                 legend_at_bottom=True) + pts_charts([pygal.StackedBar,
                                                                      pygal.Treemap,
                                                                      ],
                                                                     cumulated,
                                                                     attr,
                                                                     False,
                                                                     start_date,
                                                                     show_legend=False)

        charts_set1 = can_charts([pygal.StackedBar,
                                  pygal.Treemap],
                                 cumulated,
                                 [attr],
                                 True,
                                 start_date,
                                 legend_at_bottom=True) + can_charts([pygal.Bar,
                                                                      pygal.Treemap],
                                                                     cumulated,
                                                                     [attr],
                                                                     False,
                                                                     start_date,
                                                                     show_legend=False)

    else:

        charts_set1 = can_charts([pygal.StackedBar,
                                  pygal.Treemap],
                                 cumulated,
                                 [attr],
                                 True,
                                 start_date,
                                 show_legend=False) + can_charts([pygal.Bar,
                                                                  pygal.Treemap],
                                                                 cumulated,
                                                                 [attr],
                                                                 False,
                                                                 start_date,
                                                                 show_legend=True,
                                                                 legend_at_bottom=True)

        charts_set2 = pts_charts([pygal.StackedBar,
                                  pygal.Treemap,
                                  ],
                                 cumulated,
                                 attr,
                                 True,
                                 start_date,
                                 show_legend=False) + pts_charts([pygal.StackedBar,
                                                                  pygal.Treemap,
                                                                  ],
                                                                 cumulated,
                                                                 attr,
                                                                 False,
                                                                 start_date,
                                                                 show_legend=True,
                                                                 legend_at_bottom=True)

    pt_filename = attr + "_pt.csv"
    pt_file = pt_folder_path + pt_filename

    chart1 = pt_dateline_chart(
        pt_file,
        start_date=start_date,
        dots_size=1,
        show_legend=True,
        legend_at_bottom=True)
    chart2 = pt_cumulated_dateline_chart(
        pt_file,
        start_date=None,
        legend_at_bottom=True,
        show_legend=True,
        dots_size=1)

    page_title = "Canada - " + attr.upper()

    if attr in ["cases", "deaths", "tests_completed"]:
        return render_template(
            'charts.html',
            charts=[charts_set1[0], charts_set2[0],
                    charts_set1[2], charts_set2[2],
                    chart1, chart2,
                    charts_set1[1], charts_set2[1],
                    charts_set1[3], charts_set2[3]],
            page_title=page_title,
            updated_date=read_update_time(),
            start_date=start_date,
            attr=attr)
    else:
        return render_template(
            'charts.html',
            charts=[charts_set1[0], charts_set2[0],
                    charts_set1[2], charts_set2[2],
                    chart1, chart2, ],
            page_title=page_title,
            updated_date=read_update_time(),
            start_date=start_date,
            attr=attr)


@app.route('/pts_view/')
@app.route('/pts_view/<start_date>/')
@cache.cached(timeout=3600)
def pts_view(start_date=None):

    charts = []

    for attr in [
        "cases",
        "deaths",
        "hospitalizations",
        "icu",
        "tests_completed",
        "vaccine_coverage_dose_1",
        "vaccine_coverage_dose_2",
        "vaccine_coverage_dose_3",
        "vaccine_coverage_dose_4",
    ]:

        if attr in [
            "cases",
            "deaths",
            "tests_completed",
            "vaccine_coverage_dose_1",
            "vaccine_coverage_dose_2",
            "vaccine_coverage_dose_3",
            "vaccine_coverage_dose_4",
        ]:

            sample_by_week = True
        else:
            sample_by_week = False

        if attr in ["cases", "deaths", "tests_completed"]:
            cumulated = False
        else:
            cumulated = True

        charts.extend(pts_charts([pygal.Line],
                                  cumulated,
                                  attr,
                                  sample_by_week,
                                  start_date,
                                  show_last_item=True,
                                  show_legend=True,
                                  dots_size=1,
                                  legend_at_bottom=True))

        charts.extend(pts_charts([pygal.Treemap],
                              cumulated,
                              attr,
                              sample_by_week,
                              start_date,
                              show_last_item=False,
                              show_legend=True,
                              dots_size=1,
                              legend_at_bottom=True))

        charts.append(can_pts_summary_chart(
        pygal.HorizontalStackedBar,
        [(attr, False),],
        legend_at_bottom=True))

    return render_template(
        'charts.html',
        charts=charts,
        page_title="Provinces/Territories",
        updated_date=read_update_time())


@app.route('/pt_view/<region>')
@app.route('/pt_view/<region>/<start_date>')
@cache.cached(timeout=3600)
def pt_view(region, start_date=None):

    chart3 = pt_weekly_chart_from_attrs(region,
                                        pygal.Bar,
                                        [("deaths",
                                          False),
                                         ("hospitalizations",
                                          True),
                                         ],
                                        "")

    chart1 = pt_weekly_chart_from_attrs(region,
                                        pygal.Bar,
                                        [("hospitalizations",
                                          True),
                                         ("cases",
                                          False),
                                         ],
                                        "",)

    chart2 = pt_weekly_chart_from_attrs(region,
                                        pygal.Bar,
                                        [("deaths", False), ],
                                        "", start_date,)

    chart9 = pt_hrs_summary_chart(
        region,
        pygal.HorizontalBar,
        reversed([("cases", True), ("deaths", True)]),
        legend_at_bottom=True)

    chart4 = pt_weekly_chart_from_attrs(region,
                                        pygal.Bar,
                                        [("icu", True), ],
                                        "", start_date,)

    chart6 = pt_hrs_summary_chart(
        region,
        pygal.HorizontalStackedBar,
        reversed([("cases", False), ("deaths", False)]),
        legend_at_bottom=True)

    chart7 = pt_weekly_chart_from_attrs(region,
                                        pygal.Line,
                                        [("vaccine_administration_dose_1", True),
                                         ("vaccine_administration_dose_2", True),
                                         ("vaccine_administration_dose_3", True),
                                         ("vaccine_administration_dose_4", True), ],
                                        "", start_date,)

    chart8 = pt_weekly_chart_from_attrs(region,
                                        pygal.Line,
                                        [("vaccine_coverage_dose_1", True),
                                         ("vaccine_coverage_dose_2", True),
                                         ("vaccine_coverage_dose_3", True),
                                         ("vaccine_coverage_dose_4", True), ],
                                        "", start_date,)

    chart5 = pt_weekly_chart_from_attrs(region,
                                        pygal.Bar,
                                        [("cases",
                                          False),
                                         ("tests_completed",
                                          False)],
                                        "",
                                        start_date,)

    chart10 = pt_weekly_chart_from_attrs(region,
                                         pygal.Bar,
                                         [("hospitalizations", True)],
                                         "", start_date,)


    charts = [
        chart1,
        chart2,
        chart3,
        chart4,
        chart5,
        chart6,
        chart7,
        chart8,
        chart9,
        chart10]

    return render_template(
        'charts.html',
        charts=charts,
        page_title=region,
        updated_date=read_update_time())


@app.route('/hr_view/<region>/<sub_region_1>')
@app.route('/hr_view/<region>/<sub_region_1>/<start_date>')
@cache.cached(timeout=3600)
def hr_view(region, sub_region_1, start_date=None):

    chart1 = hr_charts(region, sub_region_1, [pygal.Bar],
                       False,
                       ["deaths"],
                       sample_by_week=True,
                       start_date=start_date,
                       show_last_item=False)

    chart2 = hr_charts(region, sub_region_1, [pygal.Bar],
                       False,
                       ["deaths", "cases"],
                       sample_by_week=True,
                       start_date=start_date,
                       show_last_item=False)

    chart3 = hr_charts(region, sub_region_1, [pygal.Bar],
                       False,
                       ["deaths"],
                       sample_by_week=False,
                       start_date=start_date,
                       show_last_item=False)

    chart4 = hr_charts(region, sub_region_1, [pygal.Bar],
                       False,
                       ["deaths", "cases"],
                       sample_by_week=False,
                       start_date=start_date,
                       show_last_item=True)    

    chart6 = hr_charts(region, sub_region_1, [pygal.Line],
                       True,
                       ["deaths", "cases"],
                       sample_by_week=False,
                       start_date=start_date,
                       show_last_item=True)

    chart5 = hr_charts(region, sub_region_1, [pygal.Line],
                       True,
                       ["deaths"],
                       sample_by_week=False,
                       start_date=start_date,
                       show_last_item=False)

    charts = chart1 + chart2 + chart3 + [chart4[0]] + chart5 + chart6 + [chart4[1]]

    return render_template(
        'charts.html',
        charts=charts,
        page_title=hr_short_name.get(
            sub_region_1, sub_region_1) + ", " + region,
        attr="cases",
        updated_date=read_update_time())


def can_weekly_chart_from_files(
        pygal_chart,
        files,
        title="",
        start_date=None,
        **kwargs):

    data_x_y = {}
    groups = {}
    if start_date is not None:
        start_week = report_date_to_year_week(start_date)

    for file, already_cumulated in files:
        with open(can_folder_path + file + "_can.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                year_week = report_date_to_year_week(row_data["date"])
                if start_date is None or year_week >= start_week:
                    if already_cumulated:
                        data_x_y[(year_week, row_data["name"])
                                 ] = float(row_data["value"])
                    else:
                        if (year_week, row_data["name"]) not in data_x_y:
                            data_x_y[(year_week, row_data["name"])] = 0
                        data_x_y[(year_week, row_data["name"])
                                 ] += float(row_data["value_daily"])
                    groups[row_data["name"]] = float(row_data["value"])

    report_weeks = set()
    for key in data_x_y:
        week = key[0]
        report_weeks.add(week)

    sorted_report_weeks = sorted(report_weeks)

    chart = pygal_chart(height=280, show_x_guides=True,
                        show_minor_x_labels=False,
                        show_x_labels=True,
                        legend_at_bottom=True,
                        x_label_rotation=0.01, **kwargs)

    for group in groups:
        timeseries_data = []
        for week in sorted_report_weeks:
            if (week, group) in data_x_y:
                year_week_str = str(week[0]) + ' ' + str(week[1])
                start_date_of_week = str(
                    datetime.datetime.strptime(
                        year_week_str + ' 1',
                        '%G %V %u'))[
                    :10]
                timeseries_data.append({"value": data_x_y[(week, group)], "xlink": {
                                       "href": request.host_url + "home/" + start_date_of_week, "target": "_top"}})
            else:
                timeseries_data.append(None)

        if start_date:
            chart.add(
                {
                    "title": group,
                    'xlink': {
                        "href": request.host_url +
                        "can_attr_view/" +
                        group +
                        "/" +
                        start_date,
                        "target": "_top"}},
                timeseries_data)
        else:
            chart.add({"title": group, 'xlink': {"href": request.host_url +
                                                 "can_attr_view/" + group, "target": "_top"}}, timeseries_data)

    chart.x_labels = sorted_report_weeks
    chart.x_labels_major = [w for w in sorted_report_weeks if w[1] == 1]

    return chart.render_data_uri()


def pt_weekly_chart_from_attrs(
        region,
        pygal_chart,
        attrs,
        title="",
        start_date=None,
        **kwargs):

    data_x_y = {}
    groups = {}
    if start_date is not None:
        start_week = report_date_to_year_week(start_date)

    for attr, already_cumulated in attrs:
        with open(pt_folder_path + attr + "_pt.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                if row_data["region"] == region:
                    year_week = report_date_to_year_week(row_data["date"])
                    if start_date is None or year_week >= start_week:
                        if already_cumulated:
                            data_x_y[(year_week, row_data["name"])
                                     ] = float(row_data["value"])
                        else:
                            if (year_week, row_data["name"]) not in data_x_y:
                                data_x_y[(year_week, row_data["name"])] = 0
                            data_x_y[(year_week, row_data["name"])
                                     ] += float(row_data["value_daily"])
                        groups[row_data["name"]] = float(row_data["value"])

    report_weeks = set()
    for key in data_x_y:
        week = key[0]
        report_weeks.add(week)

    sorted_report_weeks = sorted(report_weeks)

    chart = pygal_chart(height=280, show_x_guides=True,
                                        show_minor_x_labels=False,
                                        show_x_labels=True,
                                        legend_at_bottom=True,
                                        x_label_rotation=0.01, **kwargs)

    for group in groups:
        timeseries_data = []
        for week in sorted_report_weeks:
            if (week, group) in data_x_y:
                year_week_str = str(week[0]) + ' ' + str(week[1])
                start_date_of_week = str(
                    datetime.datetime.strptime(
                        year_week_str + ' 1',
                        '%G %V %u'))[
                    :10]
                timeseries_data.append({"value": data_x_y[(week, group)], "xlink": {
                                       "href": request.host_url + "pt_view/" + region + "/" + start_date_of_week, "target": "_top"}})
            else:
                timeseries_data.append(None)

        chart.add(
            {
                "title": group,
                'xlink': {
                    "href": request.host_url +
                    "pt_attr_view/" +
                    region +
                    "/" +
                    group,
                    "target": "_top"}},
            timeseries_data)

    chart.x_labels = sorted_report_weeks
    chart.x_labels_major = [w for w in sorted_report_weeks if w[1] == 1]
    chart.title = title

    return chart.render_data_uri()


def hr_weekly_chart_from_files(
        region,
        sub_region_1,
        pygal_chart,
        already_cumulated,
        files,
        title="",
        **kwargs):
    data_x_y = {}
    groups = {}

    for file in files:
        with open(hr_folder_path + file, 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                if row_data["region"] == region and row_data["sub_region_1"] == sub_region_1:
                    year_week = report_date_to_year_week(row_data["date"])
                    if already_cumulated:
                        data_x_y[(year_week, row_data["name"])
                                 ] = int(row_data["value"])
                    else:
                        if (year_week, row_data["name"]) not in data_x_y:
                            data_x_y[(year_week, row_data["name"])] = 0
                        data_x_y[(year_week, row_data["name"])
                                 ] += int(row_data["value_daily"])
                    groups[row_data["name"]] = int(row_data["value"])

    report_weeks = set()
    for key in data_x_y:
        week = key[0]
        report_weeks.add(week)

    sorted_report_weeks = sorted(report_weeks)

    chart = pygal_chart(height=280,
                        show_x_guides=True,
                        show_minor_x_labels=False,
                        show_x_labels=True,
                        legend_at_bottom=True,
                        x_label_rotation=0.01, **kwargs)

    for group in groups:
        timeseries_data = []
        for week in sorted_report_weeks:
            if (week, group) in data_x_y:
                timeseries_data.append(data_x_y[(week, group)])
            else:
                timeseries_data.append(None)

        chart.add({"title": group, }, timeseries_data)

    chart.x_labels = sorted_report_weeks
    chart.x_labels_major = [w for w in sorted_report_weeks if w[1] == 1]

    return chart.render_data_uri()


def hr_charts(
        region,
        sub_region_1,
        pygal_charts,
        already_cumulated,
        attrs,
        sample_by_week=True,
        start_date=None,
        show_last_item=False,
        **kwargs):

    data_x_y = {}
    groups = {}
    if sample_by_week:
        if start_date is not None:
            start_date = report_date_to_year_week(start_date)

    for attr in attrs:
        with open(hr_folder_path + attr + "_hr.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                if row_data["region"] == region and row_data["sub_region_1"] == sub_region_1:
                    if sample_by_week:
                        report_time = report_date_to_year_week(
                            row_data["date"])
                    else:
                        report_time = row_data["date"]
                    if start_date is None or report_time >= start_date:
                        if already_cumulated:
                            data_x_y[(report_time, row_data["name"])
                                     ] = int(row_data["value"])
                        else:
                            if (report_time, row_data["name"]) not in data_x_y:
                                data_x_y[(report_time, row_data["name"])] = 0
                            data_x_y[(report_time, row_data["name"])
                                     ] += int(row_data["value_daily"])
                        groups[row_data["name"]] = int(row_data["value"])

    reports = set()
    for key in data_x_y:
        report_time = key[0]
        reports.add(report_time)

    sorted_reports = sorted(reports)

    charts = []

    for pygal_chart in pygal_charts:

        if pygal_chart in [pygal.Bar, pygal.StackedBar, pygal.Line]:
            chart = pygal_chart(
                height=280,
                show_legend=True,
                show_x_guides=True,
                show_minor_x_labels=False,
                show_x_labels=True,
                x_label_rotation=0.01,
                legend_at_bottom=True,
                **kwargs)

            for group in groups:
                timeseries_data = []
                for report_time in sorted_reports:
                    if (report_time, group) in data_x_y:
                        if sample_by_week:
                            timeseries_data.append(
                                {"value": data_x_y[(report_time, group)], })
                        else:
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "hr_view/" + region + "/" + sub_region_1 + "/" + report_time, "target": "_top"}})
                    else:
                        timeseries_data.append(None)

                chart.add({"title": group, }, timeseries_data)

            if sample_by_week:
                chart.x_labels = sorted_reports
                chart.x_labels_major = [w for w in sorted_reports if w[1] == 1]
            else:
                chart.x_labels = sorted_reports
                chart.x_labels_major = [
                    d for d in sorted_reports if d[8:] == "01" and d[5:7] in ["01", "07"]]

        else:
            chart = pygal_chart(height=280, show_legend=False, **kwargs)

            for group in groups:

                timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                    report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

                chart.add({"title": group, }, timeseries_data)

        charts.append(chart.render_data_uri())

    if show_last_item:

        if already_cumulated:
            chart = pygal.HorizontalBar(
                height=280,
                show_legend=True,
                legend_at_bottom=True,
                **kwargs)
        else:
            chart = pygal.Bar(
                height=280,
                show_legend=True,
                legend_at_bottom=True,
                **kwargs)
        for group in groups:
            timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

            chart.add({"title": group, }, timeseries_data[-1:])

        charts.append(chart.render_data_uri())

    return charts


def pt_charts(
        region,
        pygal_charts,
        already_cumulated,
        attr,
        sample_by_week=True,
        start_date=None,
        **kwargs):

    data_x_y = {}
    groups = {}
    if sample_by_week:
        if start_date is not None:
            start_date = report_date_to_year_week(start_date)

    for attr in [attr]:
        with open(pt_folder_path + attr + "_pt.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                if region is None or row_data["region"] == region:
                    if sample_by_week:
                        report_time = report_date_to_year_week(
                            row_data["date"])
                    else:
                        report_time = row_data["date"]
                    if start_date is None or report_time >= start_date:
                        if already_cumulated:
                            data_x_y[(report_time, row_data["name"])
                                     ] = float(row_data["value"])
                        else:
                            if (report_time, row_data["name"]) not in data_x_y:
                                data_x_y[(report_time, row_data["name"])] = 0
                            data_x_y[(report_time, row_data["name"])
                                     ] += float(row_data["value_daily"])
                        groups[row_data["name"]] = float(row_data["value"])

    reports = set()
    for key in data_x_y:
        report_time = key[0]
        reports.add(report_time)

    sorted_reports = sorted(reports)

    charts = []

    for pygal_chart in pygal_charts:

        if pygal_chart == pygal.Bar:
            chart = pygal_chart(
                height=280,
                show_legend=False,
                show_x_guides=True,
                show_minor_x_labels=False,
                show_x_labels=True,
                x_label_rotation=0.01,
                **kwargs)

            if sample_by_week:

                for group in groups:
                    timeseries_data = []
                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            year_week_str = str(
                                report_time[0]) + ' ' + str(report_time[1])
                            start_date_of_week = str(
                                datetime.datetime.strptime(
                                    year_week_str + ' 1',
                                    '%G %V %u'))[
                                :10]
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "pt_attr_view/" + "/" + region + "/" + attr + "/" + start_date_of_week, "target": "_top"}})
                        else:
                            timeseries_data.append(None)

                    chart.add({"title": group, }, timeseries_data)

                chart.x_labels = sorted_reports
                chart.x_labels_major = [w for w in sorted_reports if w[1] == 1]
            else:

                for group in groups:
                    timeseries_data = []
                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "pt_attr_view/" + "/" + region + "/" + attr + "/" + report_time, "target": "_top"}})
                        else:
                            timeseries_data.append(None)

                    chart.add({"title": group, }, timeseries_data)

                chart.x_labels = sorted_reports
                chart.x_labels_major = [
                    d for d in sorted_reports if d[8:] == '01' and d[5:7] == '01']

        elif pygal_chart == pygal.Pie:
            chart = pygal_chart(
                height=280,
                inner_radius=.4,
                show_legend=False,
                **kwargs)

            for group in groups:

                timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                    report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

                chart.add({"title": group, }, timeseries_data)
        else:
            chart = pygal_chart(height=280, show_legend=False, **kwargs)

            for group in groups:

                timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                    report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

                chart.add({"title": group, }, timeseries_data)

        charts.append(chart.render_data_uri())

    return charts


def pts_charts(
        pygal_charts,
        already_cumulated,
        attr,
        sample_by_week,
        start_date=None,
        show_last_item=False,
        **kwargs):

    data_x_y = {}
    groups = {}

    start_date_ = start_date
    if sample_by_week:
        if start_date is not None:
            start_date = report_date_to_year_week(start_date)

    with open(pt_folder_path + attr + "_pt.csv", 'r') as file:
        csv_file = csv.DictReader(file)
        for row_data in csv_file:
            if sample_by_week:
                report_time = report_date_to_year_week(row_data["date"])
            else:
                report_time = row_data["date"]

            if start_date is None or report_time >= start_date:
                if already_cumulated:
                    data_x_y[(report_time, row_data["region"])
                             ] = float(row_data["value"])
                else:
                    if (report_time, row_data["region"]) not in data_x_y:
                        data_x_y[(report_time, row_data["region"])] = 0
                    data_x_y[(report_time, row_data["region"])
                             ] += float(row_data["value_daily"])
                groups[row_data["region"]] = float(row_data["value"])

    reports = set()
    for key in data_x_y:
        report_time = key[0]
        reports.add(report_time)

    sorted_reports = sorted(reports)
    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])

    charts = []

    for pygal_chart in pygal_charts:

        if pygal_chart in [pygal.Bar, pygal.StackedBar, pygal.Line]:
            chart = pygal_chart(
                height=280,
                # show_legend=False,
                show_x_guides=True,
                show_minor_x_labels=False,
                show_x_labels=True,
                x_label_rotation=0.01,
                **kwargs)

            if show_last_item:
                extra_chart = pygal.Bar(
                    height=280, show_legend=True, legend_at_bottom=True,)
                extra_chart.x_labels = [attr]

            if sample_by_week:

                for group in sorted_groups:

                    timeseries_data = []

                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            timeseries_data.append(
                                data_x_y[(report_time, group)])
                            update_last_data = {"value": data_x_y[(report_time, group)],
                                                "label": str(report_time)}
                        else:
                            timeseries_data.append(None)

                    if start_date:
                        chart.add(
                            {
                                "title": group,
                                'xlink': {
                                    "href": request.host_url +
                                    "pt_attr_view/" +
                                    group + "/" + attr + "/" + start_date_,
                                    "target": "_top"}},
                            timeseries_data)
                        if show_last_item:
                            extra_chart.add(
                                {
                                    "title": group,
                                    'xlink': {
                                        "href": request.host_url +
                                        "pt_attr_view/" +
                                        group + "/" + attr + "/" + start_date_,
                                        "target": "_top"}},
                                [update_last_data])

                    else:
                        chart.add(
                            {
                                "title": group,
                                'xlink': {
                                    "href": request.host_url +
                                    "pt_attr_view/" + group + "/" + attr,
                                    "target": "_top"}},
                            timeseries_data)

                        if show_last_item:
                            extra_chart.add(
                                {
                                    "title": group,
                                    'xlink': {
                                        "href": request.host_url +
                                        "pt_attr_view/" + group + "/" + attr,
                                        "target": "_top"}},
                                [update_last_data])

                chart.x_labels = sorted_reports
                chart.title = attr
                chart.x_labels_major = [w for w in sorted_reports if w[1] == 1]
            else:  # daily sample

                for group in sorted_groups:

                    timeseries_data = []

                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "pts_attr_view/" + attr + "/" + report_time, "target": "_top"}})
                            update_last_data = {"value": data_x_y[(report_time, group)],
                                                "label": str(report_time)}
                        else:
                            timeseries_data.append(None)

                    if start_date:
                        chart.add(
                            {
                                "title": group,
                                'xlink': {
                                    "href": request.host_url +
                                    "pt_attr_view/" +
                                    group +
                                    "/" +
                                    attr +
                                    "/" +
                                    start_date_,
                                    "target": "_top"}},
                            timeseries_data)
                        if show_last_item:
                            extra_chart.add(
                                {
                                    "title": group,
                                    'xlink': {
                                        "href": request.host_url +
                                        "pt_attr_view/" +
                                        group +
                                        "/" +
                                        attr +
                                        "/" +
                                        start_date_,
                                        "target": "_top"}},
                                [update_last_data])

                    else:
                        chart.add(
                            {
                                "title": group,
                                'xlink': {
                                    "href": request.host_url +
                                    "pt_attr_view/" + group + "/" + attr,
                                    "target": "_top"}},
                            timeseries_data)

                        if show_last_item:
                            extra_chart.add(
                                {
                                    "title": group,
                                    'xlink': {
                                        "href": request.host_url +
                                        "pt_view/" + group,  # + "/" + attr,
                                        "target": "_top"}},
                                [update_last_data])

                chart.x_labels = sorted_reports
                chart.x_labels_major = [
                    d for d in sorted_reports if d[8:] == '01' and d[5:7] in ['01', '07']]
                chart.title = attr
        else:

            chart = pygal_chart(height=280, show_legend=False)

            for group in sorted_groups:

                timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                    report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

                chart.add({"title": group, }, timeseries_data)


        charts.append(chart.render_data_uri())        

        if show_last_item:
            charts.append(extra_chart.render_data_uri())

    return charts


def can_charts(
        pygal_charts,
        already_cumulated,
        attrs,
        sample_by_week=True,
        start_date=None,
        **kwargs):

    data_x_y = {}
    groups = {}
    if sample_by_week:
        if start_date is not None:
            start_date = report_date_to_year_week(start_date)

    for attr in attrs:
        with open(can_folder_path + attr + "_can.csv", 'r') as file:
            csv_file = csv.DictReader(file)
            for row_data in csv_file:
                if sample_by_week:
                    report_time = report_date_to_year_week(row_data["date"])
                else:
                    report_time = row_data["date"]

                if start_date is None or report_time >= start_date:

                    if already_cumulated:
                        data_x_y[(report_time, row_data["name"])
                                 ] = float(row_data["value"])
                    else:
                        if (report_time, row_data["name"]) not in data_x_y:
                            data_x_y[(report_time, row_data["name"])] = 0
                        data_x_y[(report_time, row_data["name"])
                                 ] += float(row_data["value_daily"])
                    groups[row_data["name"]] = float(row_data["value"])

    reports = set()
    for key in data_x_y:
        report_time = key[0]
        reports.add(report_time)

    sorted_reports = sorted(reports)

    charts = []

    for pygal_chart in pygal_charts:

        if pygal_chart in [pygal.Bar, pygal.Line, pygal.StackedBar]:
            chart = pygal_chart(
                height=280,
                show_x_guides=True,
                show_minor_x_labels=False,
                show_x_labels=True,
                x_label_rotation=0.01,
                **kwargs)

            if sample_by_week:

                for group in groups:
                    timeseries_data = []
                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            year_week_str = str(
                                report_time[0]) + ' ' + str(report_time[1])
                            start_date_of_week = str(
                                datetime.datetime.strptime(
                                    year_week_str + ' 1',
                                    '%G %V %u'))[
                                :10]
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "can_attr_view/" + group + "/" + start_date_of_week, "target": "_top"}})
                        else:
                            timeseries_data.append(None)

                    chart.add({"title": group, }, timeseries_data)

                chart.x_labels = sorted_reports
                chart.x_labels_major = [w for w in sorted_reports if w[1] == 1]
            else:

                for group in groups:
                    timeseries_data = []
                    for report_time in sorted_reports:
                        if (report_time, group) in data_x_y:
                            timeseries_data.append({"value": data_x_y[(report_time, group)], "xlink": {
                                                   "href": request.host_url + "can_attr_view/" + group + "/" + report_time, "target": "_top"}})
                        else:
                            timeseries_data.append(None)

                    chart.add({"title": group, }, timeseries_data)

                chart.x_labels = sorted_reports
                chart.x_labels_major = [
                    d for d in sorted_reports if d[8:] == '01' and d[5:7] in ["01", "07"]]

        else:
            chart = pygal_chart(height=280, show_legend=False)

            for group in groups:

                timeseries_data = [{"value": data_x_y[(report_time, group)], "label": str(
                    report_time)} for report_time in sorted_reports if (report_time, group) in data_x_y]

            chart.add({"title": group, }, timeseries_data)

        charts.append(chart.render_data_uri())

    return charts


def pt_dateline_chart(filename, start_date=None, **kwargs):

    data_x_y = {}
    groups = {}

    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            report_time = row_data["date"]
            if start_date is None or report_time >= start_date:
                data_x_y[(row_data["date"], row_data["region"])] = float(
                    row_data["value_daily"])
                groups[row_data["region"]] = float(row_data["value"])

    report_days = set()
    for key in data_x_y:
        day = key[0]
        report_days.add(day)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    sorted_report_days = sorted(list(report_days))

    chart = pygal.DateLine(
        height=280,
        x_label_rotation=0.01,
        show_x_guides=True, **kwargs)

    for group in sorted_groups:
        data_list = [(date(int(day[:4]),
                           int(day[5:7]),
                           int(day[8:])),
                      data_x_y[(day, group)]) if (day, group) in data_x_y
                     else (date(int(day[:4]), int(day[5:7]), int(day[8:])), None)
                     for day in sorted_report_days]

        chart.add(group, data_list)

    chart.x_labels = [date(int(day[:4]), int(day[5:7]), int(day[8:]))
                      for day in sorted_report_days if day[8:] == "01" and day[5:7] in ["01", ]]

    return chart.render_data_uri()


def pt_cumulated_dateline_chart(filename, start_date=None, **kwargs):

    data_x_y = {}
    groups = {}

    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            report_time = row_data["date"]
            if start_date is None or report_time >= start_date:
                data_x_y[(row_data["date"], row_data["region"])] = float(
                    row_data["value"])
                groups[row_data["region"]] = float(row_data["value"])

    report_days = set()
    for key in data_x_y:
        day = key[0]
        report_days.add(day)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    sorted_report_days = sorted(list(report_days))

    chart = pygal.DateLine(
        height=280,
        x_label_rotation=0.01,
        show_x_guides=True, **kwargs)

    for group in sorted_groups:
        data_list = [(date(int(day[:4]),
                           int(day[5:7]),
                           int(day[8:])),
                      data_x_y[(day, group)]) if (day, group) in data_x_y
                     else (date(int(day[:4]), int(day[5:7]), int(day[8:])), None)
                     for day in sorted_report_days]

        chart.add(group, data_list)

    chart.x_labels = [date(int(day[:4]), int(day[5:7]), int(day[8:]))
                      for day in sorted_report_days if day[8:] == "01" and day[5:7] in ["01", ]]

    return chart.render_data_uri()


def pt_summary_chart(pygal_chart_class, filename, **kwargs):

    pt_value = {}
    pt_date = {}
    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            pt_value[row_data["region"]] = int(
                row_data["value"])
            pt_date[row_data["region"]] = row_data["date"]

        sorted_pts = sorted(pt_value.keys(), key=lambda k: -pt_value[k])
        chart = pygal_chart_class(height=280, **kwargs)
        chart.x_labels = [row_data["name"]]
        for pt in sorted_pts:
            chart.add({"title": pt,
                       'xlink': {"href": request.host_url + "pt_view/" + pt,
                                 "target": "_top"}},
                      [{"value": pt_value[pt],
                        "label": pt_date[pt]}])
        return chart.render_data_uri()


def can_pts_summary_chart(pygal_chart_class, attrs, **kwargs):

    pt_value = {}
    pt_date = {}
    pts = set()
    names = []
    for attr, value_daily in attrs:
        filename = pt_folder_path + attr + "_pt.csv"
        with open(filename, 'r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                row_data = dict(row)
                pts.add(row_data["region"])
                if value_daily:
                    pt_value[(row_data["name"], row_data["region"])
                             ] = float(row_data["value_daily"])
                else:
                    pt_value[(row_data["name"], row_data["region"])
                             ] = float(row_data["value"])
                pt_date[(row_data["name"], row_data["region"])
                        ] = row_data["date"]
            names.append(row_data["name"])

    sorted_pts = sorted(list(pts), key=lambda k: -
                        sum([pt_value[(name, k)] for name in names]))

    chart = pygal_chart_class(height=280, **kwargs)
    for pt in sorted_pts:
        data = [{"value": pt_value[(name, pt)], "label": pt_date[(name, pt)],
                 "xlink": {"href": request.host_url + "pt_attr_view/" + pt + "/" + name,
                           "target": "_top"}}
                for name in names]
        chart.add({"title": pt,
                   'xlink': {"href": request.host_url + "pt_view/" + pt,
                             "target": "_top"}}, data)
    chart.x_labels = names

    return chart.render_data_uri()


def pt_hrs_summary_chart(region, pygal_chart_class, attrs, **kwargs):

    hr_value = {}
    hr_date = {}
    hrs = set()
    names = []
    for file, value_daily in attrs:
        filename = hr_folder_path + file + "_hr.csv"
        with open(filename, 'r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                row_data = dict(row)
                if row_data["region"] == region:
                    hrs.add(row_data["sub_region_1"])
                    if value_daily:
                        hr_value[(row_data["name"], row_data["sub_region_1"])] = int(
                            row_data["value_daily"])
                    else:
                        hr_value[(row_data["name"], row_data["sub_region_1"])] = int(
                            row_data["value"])
                    hr_date[(row_data["name"],
                             row_data["sub_region_1"])] = row_data["date"]
            names.append(row_data["name"])

    sorted_hrs = sorted(list(hrs), key=lambda k: -
                        sum([hr_value.get((name, k), 0) for name in names]))
    chart = pygal_chart_class(height=280, **kwargs)
    for hr in sorted_hrs:
        data = [{"value": hr_value.get((name, hr), None), "label": hr_date.get(
            (name, hr), None)} for name in names]
        chart.add({"title": hr_short_name.get(hr, hr),
                   'xlink': {"href": request.host_url + "hr_view/" + region + "/" + hr,
                             "target": "_top"}}, data)
    chart.x_labels = names

    return chart.render_data_uri()


def hr_summary_chart(region, pygal_chart_class, filename, **kwargs):

    hr_value = {}
    hr_date = {}
    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            if row_data["region"] == region:
                hr_value[row_data["sub_region_1"]] = int(
                    row_data["value"])
                hr_date[row_data["sub_region_1"]] = row_data["date"]

        sorted_hrs = sorted(hr_value.keys(), key=lambda k: -hr_value[k])
        chart = pygal_chart_class(height=280, **kwargs)
        chart.x_labels = [row_data["name"]]
        for hr in sorted_hrs:
            chart.add({"title": hr_short_name.get(hr,
                                                  hr),
                       'xlink': {"href": request.host_url + "hr_view/" + region + "/" + hr,
                                 "target": "_top"}},
                      [{"value": hr_value[hr],
                        "label": hr_date[hr]}])
        return chart.render_data_uri()


def hr_summary_chart2(
        region,
        sub_region_1,
        pygal_chart_class,
        value_daily,
        files,
        **kwargs):

    hr_value = {}
    hr_date = {}
    names = []
    for file in files:
        filename = hr_folder_path + file
        with open(filename, 'r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                row_data = dict(row)
                if row_data["region"] == region and row_data["sub_region_1"] == sub_region_1:
                    if value_daily:
                        hr_value[row_data["name"]] = int(
                            row_data["value_daily"])
                    else:
                        hr_value[row_data["name"]] = int(row_data["value"])
                    hr_date[row_data["name"]] = row_data["date"]
            names.append(row_data["name"])

    chart = pygal_chart_class(height=280, **kwargs)

    for name in names:
        data = [{"value": hr_value[name], "label": hr_date[name]}]
        chart.add(
            {
                "title": name,
                'xlink': {
                    "href": request.host_url +
                    "hr_attr_view/" +
                    region +
                    "/" +
                    sub_region_1 +
                    "/" +
                    name,
                    "target": "_top"}},
            data)

    if value_daily:
        chart.x_labels = ["value_daily"]
    else:
        chart.x_labels = ["value"]

    return chart.render_data_uri()


def hr_dateline_chart(filename):

    data_x_y = {}
    groups = {}

    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            data_x_y[(row_data["date"], row_data["sub_region_1"])] = int(
                row_data["value_daily"])
            groups[row_data["sub_region_1"]] = int(row_data["value"])

    report_days = set()
    for key in data_x_y:
        day = key[0]
        report_days.add(day)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    sorted_report_days = sorted(list(report_days))

    chart = pygal.DateLine(
        height=280,
        dots_size=1,
        show_legend=True,
        x_label_rotation=0.01,
        show_x_guides=True)

    for group in sorted_groups:
        data_list = [(date(int(day[:4]),
                           int(day[5:7]),
                           int(day[8:])),
                      data_x_y[(day, group)]) if (day, group) in data_x_y
                     else (date(int(day[:4]), int(day[5:7]), int(day[8:])), None)
                     for day in sorted_report_days]

        chart.add(group, data_list)

    chart.x_labels = [date(int(day[:4]), int(day[5:7]), int(day[8:]))
                      for day in sorted_report_days if day[8:] == "01" and day[5:7] in ["01", ]]

    return chart.render_data_uri()


def hrs_chart(attr, sample_by_week=True, **kwargs):

    data_x_y = {}
    groups = {}

    with open(hr_folder_path + attr + "_hr.csv", 'r') as file:
        csv_file = csv.DictReader(file)
        for row_data in csv_file:
            if sample_by_week or row_data["date"] >= "2022-07-01":
                if sample_by_week:
                    report_time = report_date_to_year_week(row_data["date"])
                else:
                    report_time = row_data["date"]
                if (report_time, row_data["sub_region_1"]) not in data_x_y:
                    data_x_y[(report_time, row_data["sub_region_1"])] = 0
                data_x_y[(report_time, row_data["sub_region_1"])
                         ] += int(row_data["value_daily"])
                groups[row_data["sub_region_1"]] = float(row_data["value"])

    reports = set()
    for key in data_x_y:
        report_time = key[0]
        reports.add(report_time)

    sorted_reports = sorted(reports)

    chart = pygal.StackedBar(
        height=280,
        show_x_guides=True,
        show_minor_x_labels=False,
        show_x_labels=True,
        x_label_rotation=0.01, **kwargs)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    for group in sorted_groups:
        timeseries_data = []
        for report_time in sorted_reports:
            if (report_time, group) in data_x_y:
                timeseries_data.append(data_x_y[(report_time, group)])
            else:
                timeseries_data.append(None)

        chart.add({"title": group}, timeseries_data)

    chart.x_labels = sorted_reports

    chart.title = attr

    if sample_by_week:
        chart.x_labels_major = [w for w in sorted_reports if w[1] == 1]
    else:
        chart.x_labels_major = [
            d for d in sorted_reports if d[8:] == "01" and d[5:7] in ["01", "07"]]
    return chart.render_data_uri()


def hr_chart(pygal_chart_class, attr, **kwargs):

    hr_value = {}
    with open(hr_folder_path + attr + "_hr.csv", 'r') as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            row_data = dict(row)
            hr_value[(row_data["region"], row_data["sub_region_1"])] = float(
                row_data["value"])

        sorted_hrs = sorted(
            hr_value.keys(),
            key=lambda k: -hr_value[k])
        chart = pygal_chart_class(height=280, **kwargs)
        for k in sorted_hrs:
            if k[1] in hr_short_name:
                name = k[0] + "," + hr_short_name[k[1]]
            else:
                name = k[0] + "," + k[1]
            chart.add({"title": name,
                       "xlink": {"href": request.host_url + "hr_view/" + k[0] + "/" + k[1],
                                 "target": "_top"}},
                      [{"value": hr_value[k],
                        "xlink": {"href": request.host_url + "hr_view/" + k[0] + "/" + k[1],
                                  "target": "_top"}}])

        return chart.render_data_uri()


def pts_weekly_chart(
        pygal_chart,
        already_cumulated,
        filename,
        title="",
        **kwargs):

    data_x_y = {}
    groups = {}

    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row_data in csv_file:
            year_week = report_date_to_year_week(row_data["date"])
            if already_cumulated:
                data_x_y[(year_week, row_data["region"])
                         ] = int(row_data["value"])
            else:
                if (year_week, row_data["region"]) not in data_x_y:
                    data_x_y[(year_week, row_data["region"])] = 0
                data_x_y[(year_week, row_data["region"])
                         ] += int(row_data["value_daily"])
            groups[row_data["region"]] = int(row_data["value"])

    report_weeks = set()
    for key in data_x_y:
        week = key[0]
        report_weeks.add(week)

    sorted_report_weeks = sorted(report_weeks)

    chart = pygal_chart(height=280, **kwargs)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    for group in sorted_groups:
        if pygal_chart in [pygal.Treemap, pygal.Pie]:
            timeseries_data = [{"value": data_x_y[(week, group)], "label": str(
                week)} for week in sorted_report_weeks if (week, group) in data_x_y]
        else:
            timeseries_data = []
            for week in sorted_report_weeks:
                if (week, group) in data_x_y:
                    timeseries_data.append(data_x_y[(week, group)])
                else:
                    timeseries_data.append(None)
        chart.add(group, timeseries_data)

    chart.title = title
    if pygal_chart == pygal.Box:
        chart.x_labels = sorted_groups
    else:
        chart.x_labels = sorted_report_weeks
        if pygal_chart in [pygal.Bar, pygal.StackedBar, pygal.Radar]:
            chart.x_labels_major = [
                w for w in sorted_report_weeks if w[1] == 1]

    return chart.render_data_uri()


def pt_hr_chart(pygal_chart, filename, title="", **kwargs):

    data_x_y = {}
    groups = {}
    hrs = {}
    regions = {}

    with open(filename, 'r') as file:
        csv_file = csv.DictReader(file)
        for row_data in csv_file:
            hr = row_data["sub_region_1"]
            if (hr, row_data["region"]) not in data_x_y:
                data_x_y[(hr, row_data["region"])] = 0
            data_x_y[(hr, row_data["region"])] += int(row_data["value_daily"])
            groups[row_data["region"]] = groups.get(
                row_data["region"], 0) + int(row_data["value_daily"])
            hrs[row_data["sub_region_1"]] = hrs.get(
                row_data["sub_region_1"], 0) + int(row_data["value_daily"])
            regions[row_data["sub_region_1"]] = row_data["region"]

    report_hrs = set()
    for key in data_x_y:
        hr = key[0]
        report_hrs.add(hr)

    sorted_report_hrs = sorted(
        report_hrs,
        key=lambda hr: -
        hrs[hr] if hr != "999" else 0)

    chart = pygal_chart(height=280, **kwargs)

    sorted_groups = sorted(groups.keys(), key=lambda k: -groups[k])
    for group in sorted_groups:
        if pygal_chart in [pygal.Treemap, pygal.Pie]:
            timeseries_data = [{"value": data_x_y[(hr, group)], "label": hr_short_name.get(
                str(hr), "Unknown")} for hr in sorted_report_hrs if (hr, group) in data_x_y]
        else:
            timeseries_data = []
            for hr in sorted_report_hrs:
                if (hr, group) in data_x_y:
                    timeseries_data.append(data_x_y[(hr, group)])
                else:
                    timeseries_data.append(None)
        chart.add(group, timeseries_data)

    chart.title = title
    if pygal_chart == pygal.Box:
        chart.x_labels = sorted_groups
    else:
        chart.x_labels = sorted_report_hrs
        if pygal_chart in [pygal.Bar, pygal.StackedBar, pygal.Radar]:
            chart.x_labels_major = [
                d for d in sorted_report_hrs if d[8:] == '01']

    return chart.render_data_uri()


def read_update_time():
    with open("data/CovidTimelineCanada/update_time.txt", "r") as f:
        return f.read()


def report_date_to_year_week(date):
    l = date.split("-")
    d = datetime.date(int(l[0]), int(l[1]), int(l[2]))
    cal = d.isocalendar()
    return cal[:2]
