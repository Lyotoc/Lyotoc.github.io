document.addEventListener('DOMContentLoaded', function () {
    const datetimeInput = document.getElementById('datetime');
    const idInput = document.getElementById('id');
    const resultDiv = document.getElementById('result');
    const copyBtn = document.getElementById('copy-btn');
    const datetimeError = document.getElementById('datetime-error');
    const idError = document.getElementById('id-error');

    // 验证ISO 8601日期时间格式
    function isValidDateTime(datetime) {
        const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/;
        return isoRegex.test(datetime) && !isNaN(new Date(datetime).getTime());
    }

    // 验证24位16进制ID
    function isValidId(id) {
        const hexRegex = /^[0-9a-fA-F]{24}$/;
        return hexRegex.test(id);
    }

    // 计算函数
    function calculate(datetime, id) {
        try {
            const minutes = Math.floor((new Date(datetime).getTime() / (1000 * 60)) % 1440);
            const idPart = parseInt(BigInt('0x' + id) % BigInt(100));
            return minutes * 100 + idPart;
        } catch (e) {
            return null;
        }
    }

    // 更新计算结果
    function updateResult() {
        const datetime = datetimeInput.value.trim();
        const id = idInput.value.trim();

        // 重置错误信息
        datetimeError.textContent = '';
        idError.textContent = '';

        let valid = true;

        // 验证日期时间
        if (datetime && !isValidDateTime(datetime)) {
            datetimeError.textContent = 'Invalid ISO 8601 format (e.g. 2025-03-29T04:00:00.000Z)';
            valid = false;
        }

        // 验证ID
        if (id && !isValidId(id)) {
            idError.textContent = 'Invalid ID format (16 characters hex)';
            valid = false;
        }

        // 计算并显示结果
        if (valid && datetime && id) {
            const result = calculate(datetime, id);
            if (result !== null) {
                resultDiv.textContent = result;
            } else {
                resultDiv.textContent = 'Error in calculation';
            }
        } else if (!datetime || !id) {
            resultDiv.textContent = '-';
        }
    }

    // 复制结果
    copyBtn.addEventListener('click', function() {
        if (resultDiv.textContent !== '-' && resultDiv.textContent !== 'Error in calculation') {
            const prefixSelect = document.getElementById('prefix-select');
            const prefix = prefixSelect.value;
            const textToCopy = prefix + resultDiv.textContent;
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        }
    });

    // 逆向计算时间
    document.getElementById('reverse-btn').addEventListener('click', function() {
        const reverseCodeInput = document.getElementById('reverse-code').value.trim();
        const reverseResultDiv = document.getElementById('reverse-result');
        
        // 去除前缀
        const code = reverseCodeInput.replace(/^(sceneTimingWh_|sceneSun_|sceneDelay_)/, '');
        
        if (!code || isNaN(code)) {
            reverseResultDiv.textContent = 'Invalid code';
            return;
        }

        const minutes = Math.floor(parseInt(code) / 100);
        const baseTime = minutes * 60 * 1000; // 转换为毫秒
        
        // 计算最近3天可能的时间
        const now = new Date();
        const results = [];
        for (let i = -1; i <= 1; i++) {
            const date = new Date(now);
            date.setDate(date.getDate() + i);
            const dayStart = new Date(date.setHours(0, 0, 0, 0)).getTime();
            const possibleTime = new Date(dayStart + baseTime);
            results.push(possibleTime.toISOString());
        }

        reverseResultDiv.innerHTML = results.join('<br>');
    });

    // 监听输入变化
    datetimeInput.addEventListener('input', updateResult);
    idInput.addEventListener('input', updateResult);
});
