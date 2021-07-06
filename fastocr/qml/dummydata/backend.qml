import QtQuick 2.3

// 以下是模拟数据用于 qmlscene 加载
QtObject {
    property string appid: 'mocked_appid'
    property string apikey: 'mocked_apikey'
    property string seckey: 'mocked_seckey'
    property string yd_appid: 'mocked yd_appid'
    property string yd_seckey: 'mocked yd_seckey'
    property string face_apikey: 'mocked face_apikey'
    property string face_apisec: 'mocked face_apisec'
    property string icon_theme: 'auto'
    property bool accurate: false
    property int mode: 0
    property var languages: ['JAP']
    property string default_backend: 'baidu'
    property var all_language_tags: ['JAP', 'KOR', 'FRE', 'SPA', 'GER', 'RUS']
    property var all_language_names: ['Japanese', 'Korea', 'French', 'Spanish', 'Germany', 'Russian']
    property string appver: '0.0.1-mocked'
    property var about_data: [
        { name: 'Qt', value: '5.1.0' }
    ]

    function save() {
        console.log('mocked save')
    }

    function open_setting_file() {
        console.log('mocked open_setting_file')
    }
}
