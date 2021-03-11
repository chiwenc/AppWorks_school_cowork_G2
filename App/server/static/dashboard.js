function draw_user_behavior_funnel(behavior_count) {
    var gd = document.getElementById('user_behavior_funnel');
    var data = [{
        type: 'funnel',
        y: ["View", "View Item", "Add to Cart", "Checkout"],
        x: behavior_count,
    }];
    var layout = {margin: {l: 150}, width: 600, height: 500}
    Plotly.newPlot('user_behavior_funnel', data, layout);
}

function draw_user_statistic(user_count) {
    var data = [
        {
            x: ['all_user', 'active_user', 'new_user', 'return_user'],
            y: user_count,
            type: 'bar'
        }
    ];
    Plotly.newPlot('user_statistic', data);
}

async function refresh(date) {
    console.log("refresh by date:", date);
    const data = await Promise.resolve($.ajax('/api/1.0/user/behavior/' + date))
    draw_user_behavior_funnel(data.behavior_count);
    draw_user_statistic(data.user_count);
}

let interval;
function init() {
    $('#datetimepicker').datetimepicker({  
        format: 'YYYY-MM-DD',  
        locale: moment.locale('zh-tw'),
        defaultDate: moment(),
    })
    .on('dp.change', async function(e) {
        const chosen_date = $('#datetimepicker_input')[0].value;
        const today = moment().format('YYYY-MM-DD');
        if (chosen_date == today) {
            refresh(chosen_date);
            interval = setInterval(function() {
                refresh(chosen_date);
            }, 5000);
        } else {
            clearInterval(interval);
            refresh(chosen_date);
        }
    })
}

async function main() {
    init();
    const today = moment().format('YYYY-MM-DD');
    clearInterval(interval);
    refresh(today);
    interval = setInterval(function() {
        refresh(today);
    }, 5000);
}
main();