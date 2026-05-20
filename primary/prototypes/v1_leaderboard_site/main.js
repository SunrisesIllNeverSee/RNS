
document.getElementById("statsForm").addEventListener("submit", function(event){
    event.preventDefault();
    const age = parseFloat(document.getElementById("accountAge").value);
    const msgs = parseFloat(document.getElementById("totalMessages").value);
    const vol = parseFloat(document.getElementById("messageVolume").value);
    const tt = parseFloat(document.getElementById("tokenThroughput").value);
    const sd = parseFloat(document.getElementById("sessionDepth").value);
    const pc = parseFloat(document.getElementById("promptComplexity").value);
    const cr = parseFloat(document.getElementById("compressionRatio").value);
    const ct = parseFloat(document.getElementById("crossThread").value);

    const avg = { age: 120, msgs: 600, vol: 50, tt: 70, sd: 3.5, pc: 60, cr: 0.65, ct: 2 };
    const diff = {
        age: ((age - avg.age) / avg.age * 100).toFixed(1),
        msgs: ((msgs - avg.msgs) / avg.msgs * 100).toFixed(1),
        vol: ((vol - avg.vol) / avg.vol * 100).toFixed(1),
        tt: ((tt - avg.tt) / avg.tt * 100).toFixed(1),
        sd: ((sd - avg.sd) / avg.sd * 100).toFixed(1),
        pc: ((pc - avg.pc) / avg.pc * 100).toFixed(1),
        cr: ((cr - avg.cr) / avg.cr * 100).toFixed(1),
        ct: ((ct - avg.ct) / avg.ct * 100).toFixed(1)
    };

    const result = `
        Compared to the global average:<br>
        - Account Age: ${diff.age}%<br>
        - Total Messages: ${diff.msgs}%<br>
        - Message Volume: ${diff.vol}%<br>
        - Token Throughput: ${diff.tt}%<br>
        - Session Depth: ${diff.sd}%<br>
        - Prompt Complexity: ${diff.pc}%<br>
        - Compression Ratio: ${diff.cr}%<br>
        - Cross-Thread Referencing: ${diff.ct}%
    `;

    document.getElementById("vcardContent").innerHTML = result;
    document.getElementById("vcardOutput").style.display = "block";
});
