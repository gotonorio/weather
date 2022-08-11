"""
https://www.city.kawasaki.jp/170/page/0000009578.html
https://www.data.jma.go.jp/gmd/risk/obsdl/index.php
- 気象庁のCSVデータはヘッダーを削除する。
programming by N.Goto (2022-08-11)
"""
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def main(graph_type='plt') -> None:
    # データ数が500以上の場合、表示を制限する。
    pd.set_option('display.max_rows', 500)
    # 小数点以下1桁とする。
    pd.options.display.precision = 1
    # csvデータを読み込んでDataFrameを作成する。
    df = read_csv_data('./data/hiyoshi.csv')

    # 読み込んだデータのスタート年と最終年を求める。
    start_year = df.index.year.min()
    end_year = df.index.year.max()

    if graph_type == 'plt':
        # matplotlibによるグラフ表示
        # plt.style.use('ggplot')
        plt.rcParams['font.family'] = 'Ricty Diminished'
        # 降水量
        plot_rain_fall_plt(df, start_year, end_year)
        # 降水日数
        plot_rainy_days_plt(df, start_year, end_year, 1)
    else:
        # plotlyによるグラフ表示
        plot_original_data_px(df, 650, 950, 'オリジナルデータ')
        plot_rain_amount_px(df, start_year, end_year, 650, 950, '降雨量')
        plot_rainy_days_px(df, start_year, end_year, 650, 950, '降雨日数')


def read_csv_data(fn) -> pd.core.frame.DataFrame:
    """ csvデータを読み込んで、DataFrameとして返す
    気象庁ホームページから降水量データをダウンロードする。
    気象庁のCSVデータはヘッダーを削除しておく。
    """
    char_code = 'utf_8'
    # 1列目をDatetimeIndexとして読み込む。
    df = pd.read_csv(fn, encoding=char_code, parse_dates=True,
                     index_col=0, header=None, usecols=[0, 1], skiprows=0, sep=",")
    df.columns = ['降水量']

    # データ数が500以上の場合、表示を制限する。
    pd.set_option('display.max_rows', 500)
    # 小数点以下1桁とする。
    pd.options.display.precision = 1
    return df


def create_year_df(df, yyyy=2015) -> pd.core.frame.DataFrame:
    """ 特定の年を抽出して、indexを月とするDataFrameを作る """
    df_name = f'w{yyyy}'
    df_name = df[df.index.year == yyyy]
    df_name.index = ['1月', '2月', '3月', '4月', '5月', '6月',
                     '7月', '8月', '9月', '10月', '11月', '12月']
    df_name.columns = [yyyy]
    return df_name


def plot_rain_fall_plt(df, start_year, end_year) -> None:
    """ 月毎の合計降雨量をグラフ化 """
    amount_df = df.resample('M').sum()
    # 空のDataFrameを作成。
    new_df = pd.DataFrame(index=[], columns=[])
    # 月をIndexとするDataFrameを作成。
    for y in range(start_year, end_year, 1):
        df_name = create_year_df(amount_df, y)
        new_df = pd.concat([new_df, df_name], axis=1)
    # グラフ表示
    new_df.plot.bar(title='日吉の降水量', xlabel='月', ylabel='降雨量', rot=0,
                    figsize=(10, 6), fontsize='12', width=0.8)
    # plt.savefig('降水量.png')
    # plt.show()


def plot_rainy_days_plt(df, start_year, end_year, rf=0) -> None:
    """ 月毎の降雨日数をグラフ化 """
    # 降水量が0以上の日をグラフ化
    count_df = df[df['降水量'] > rf].resample('M').count()
    # 空のDataFrameを作成。
    new_df = pd.DataFrame(index=[], columns=[])
    # 月をIndexとするDataFrameを作成。
    for y in range(start_year, end_year, 1):
        df_name = create_year_df(count_df, y)
        new_df = pd.concat([new_df, df_name], axis=1)
    # 確認のため。
    # print(new_df)
    # グラフ表示
    new_df.plot.bar(title='日吉の降水日数', xlabel='月', ylabel='降雨日数',
                    rot=0, figsize=(10, 6), fontsize='12', width=0.8)
    # plt.savefig('降水日数.png')
    plt.show()


def plot_original_data_px(df, height=650, width=950, title='無題') -> None:
    """ オリジナルデータを表示 """
    fig = px.line(df, height=height, width=950, title=title)

    fig.update_layout(font_size=14, hoverlabel_font_size=14, hoverlabel_font_color='white',
                      xaxis_title='日付', yaxis_title='降水量',
                      xaxis_title_font_size=14, yaxis_title_font_size=14)

    fig.show()


def plot_rain_amount_px(df, start_year, end_year, height=650, width=950, title='無題') -> None:
    """ 降水量グラフ表示 """
    # 年月毎の合計降雨量（月で集約して合計する）
    df_monthly_total = df.resample('M').sum()

    # 空のDataFrameを作成。
    new_df = pd.DataFrame(index=[], columns=[])
    # 月をIndexとするDataFrameを作成。
    for y in range(start_year, end_year, 1):
        df_name = create_year_df(df_monthly_total, y)
        new_df = pd.concat([new_df, df_name], axis=1)

    fig = px.bar(new_df, barmode='group', height=height, width=width, title=title)

    fig.update_layout(font_size=14, hoverlabel_font_size=14, hoverlabel_font_color='white',
                      xaxis_title='月別', yaxis_title='降水量',
                      xaxis_title_font_size=14, yaxis_title_font_size=14)

    fig.show()


def plot_rainy_days_px(df, start_year, end_year, height=650, width=950, title='無題') -> None:
    """ 降水日数グラフ表示 """
    # 月毎の降雨日数（月で集約して合計する）
    df_rainy_days = df[df['降水量'] > 0].resample('M').count()
    # print(df_count)
    # 空のDataFrameを作成。
    new_df = pd.DataFrame(index=[], columns=[])
    # 月をIndexとするDataFrameを作成。
    for y in range(start_year, end_year, 1):
        # df_name = y
        df_name = create_year_df(df_rainy_days, y)
        new_df = pd.concat([new_df, df_name], axis=1)

    fig = px.bar(new_df, barmode='group',  height=650, width=950, title=title)
    fig.update_layout(font_size=14, hoverlabel_font_size=14, hoverlabel_font_color='white',
                      xaxis_title='月別', yaxis_title='降雨日数',
                      xaxis_title_font_size=14, yaxis_title_font_size=14)

    fig.show()


if __name__ == "__main__":
    """ plotlyでグラフ表示の場合は、main('px')とする。 """
    main()
