document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('view-rules').addEventListener('click', function() {
        fetch('/rules')
            .then(response => response.json())
            .then(data => {
                let output = formatRules(data);
                document.getElementById('result').innerHTML = output;
            });
    });

    document.getElementById('search-mistake').addEventListener('click', function() {
        const mistake = document.getElementById('mistake-input').value;
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mistake: mistake })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerText = data.correction;
        });
    });
});

function formatRules(rules) {
    const order = [
        "When to Perform Sujood As-Sahw",
        "When Sujood As-Sahw Expires",
        "Following the Imam in Forgetfulness",
        "Correcting Missed Actions",
        "Forgetfulness in Shaf’ and Witr",
        "More Rules on Forgetfulness",
        "Conclusion"
    ];

    let html = '<h2>Rules</h2>';
    order.forEach(section => {
        if (rules[section]) {
            html += `<h3>${section}</h3>`;
            let content = rules[section];
            if (typeof content === 'object') {
                if (Array.isArray(content)) {
                    html += '<ul>';
                    content.forEach(item => {
                        html += `<li>${item}</li>`;
                    });
                    html += '</ul>';
                } else {
                    for (let subSection in content) {
                        html += `<h4>${subSection}</h4>`;
                        let details = content[subSection];
                        if (Array.isArray(details)) {
                            html += '<ul>';
                            details.forEach(detail => {
                                html += `<li>${detail}</li>`;
                            });
                            html += '</ul>';
                        } else {
                            html += `<p>${details}</p>`;
                        }
                    }
                }
            } else {
                html += `<p>${content}</p>`;
            }
        }
    });
    return html;
}