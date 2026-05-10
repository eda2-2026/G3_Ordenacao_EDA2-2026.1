const API_URL = '/api/sort';

const ALGO_LABELS = {
    merge: 'Merge Sort',
    quick: 'Quick Sort',
    heap: 'Heap Sort',
};

let dadosCSV = null;

function labelAlgoritmo(chave) {
    return ALGO_LABELS[chave] || chave;
}

function showToast(message, variant = 'default') {
    const region = document.getElementById('toastRegion');
    const el = document.createElement('div');
    el.className = variant === 'error' ? 'toast toast--error' : 'toast';
    el.textContent = message;
    region.appendChild(el);
    const ttl = variant === 'error' ? 9000 : 5000;
    setTimeout(() => {
        el.remove();
    }, ttl);
}

async function processCsvFile(file) {
    if (!file) return;
    const name = file.name.toLowerCase();
    if (!name.endsWith('.csv') && file.type && file.type !== 'text/csv' && file.type !== 'application/vnd.ms-excel') {
        showToast('Envie um arquivo .csv.', 'error');
        return;
    }

    document.getElementById('fileInfo').textContent = file.name;

    const text = await file.text();
    const linhas = text.split(/\n/);
    const primeira = linhas[0] ?? '';
    const cabecalho = primeira.split(',');

    const select = document.getElementById('coluna');
    select.innerHTML = '';
    cabecalho.forEach((col, idx) => {
        const option = document.createElement('option');
        option.value = String(idx);
        const rotulo = col.trim() || `Coluna ${idx}`;
        option.textContent = `${rotulo} (índice ${idx})`;
        select.appendChild(option);
    });

    dadosCSV = text;
}

const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    await processCsvFile(file);
});

const dropzone = document.querySelector('.file-dropzone');
if (dropzone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((ev) => {
        dropzone.addEventListener(ev, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    dropzone.addEventListener('dragover', () => {
        dropzone.classList.add('file-dropzone--active');
    });
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('file-dropzone--active');
    });
    dropzone.addEventListener('drop', async (e) => {
        dropzone.classList.remove('file-dropzone--active');
        const file = e.dataTransfer.files[0];
        await processCsvFile(file);
        try {
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
        } catch {
            /* alguns navegadores podem bloquear atribuição; dados já estão em dadosCSV */
        }
    });
}

const ordenarBtn = document.getElementById('ordenarBtn');

ordenarBtn.addEventListener('click', async () => {
    if (!dadosCSV) {
        showToast('Selecione um arquivo CSV primeiro.', 'error');
        return;
    }

    const coluna = document.getElementById('coluna').value;
    const tipo = document.getElementById('tipo').value;
    const reverso = document.getElementById('reverso').checked;

    const algoritmos = [];
    if (document.getElementById('alg_merge').checked) algoritmos.push('merge');
    if (document.getElementById('alg_quick').checked) algoritmos.push('quick');
    if (document.getElementById('alg_heap').checked) algoritmos.push('heap');

    if (algoritmos.length === 0) {
        showToast('Marque pelo menos um algoritmo.', 'error');
        return;
    }

    const loading = document.getElementById('loading');
    const resultadosDiv = document.getElementById('resultados');

    loading.style.display = 'flex';
    ordenarBtn.disabled = true;
    resultadosDiv.style.display = 'none';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                csv: dadosCSV,
                coluna: parseInt(coluna, 10),
                tipo,
                reverso,
                algoritmos,
            }),
        });

        const raw = await response.text();
        let data;
        try {
            data = JSON.parse(raw);
        } catch {
            data = null;
        }

        if (!response.ok) {
            const msg =
                (data && (data.message || data.error)) ||
                `Erro ${response.status}: não foi possível ordenar.`;
            showToast(msg, 'error');
            return;
        }

        if (!data || typeof data.tempos !== 'object') {
            showToast('Resposta inválida do servidor.', 'error');
            return;
        }

        mostrarResultados(data);
        resultadosDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
        console.error('Erro:', error);
        simularOrdenacaoLocal(dadosCSV, coluna, tipo, reverso, algoritmos);
        resultadosDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } finally {
        loading.style.display = 'none';
        ordenarBtn.disabled = false;
    }
});

function mostrarResultados(data) {
    const resultadosDiv = document.getElementById('resultados');
    const temposTable = document.getElementById('temposTable');
    const downloadsDiv = document.getElementById('downloads');

    const tempos = data.tempos;
    const entries = Object.entries(tempos);
    const maisRapido =
        entries.length > 0
            ? entries.reduce((a, b) => (tempos[a[0]] < tempos[b[0]] ? a : b))[0]
            : null;

    temposTable.innerHTML = `
        <h3>Tempos de execução</h3>
        <div class="tempos-grid"></div>
    `;
    const grid = temposTable.querySelector('.tempos-grid');

    for (const [algoritmo, tempo] of entries) {
        const isMaisRapido = algoritmo === maisRapido;
        const card = document.createElement('div');
        card.className = `tempo-card${isMaisRapido ? ' mais-rapido' : ''}`;
        card.innerHTML = `
            <h4>${labelAlgoritmo(algoritmo)}</h4>
            <div class="tempo">${tempo.toFixed(6)} <span class="tempo-unit">segundos</span></div>
            ${isMaisRapido ? '<div class="status">Menor tempo nesta execução</div>' : ''}
        `;
        grid.appendChild(card);
    }

    downloadsDiv.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'downloads-region-inner';

    const title = document.createElement('h3');
    title.textContent = 'Baixar CSVs ordenados';
    wrap.appendChild(title);

    const linksRow = document.createElement('div');
    linksRow.className = 'download-links';

    for (const [algoritmo, arquivo] of Object.entries(data.arquivos || {})) {
        const link = document.createElement('a');
        link.href = `data:text/csv;charset=utf-8,${encodeURIComponent(arquivo)}`;
        link.download = `ordenado_${algoritmo}.csv`;
        link.className = 'download-link';
        link.textContent = `Baixar ${labelAlgoritmo(algoritmo)}`;
        linksRow.appendChild(link);
    }

    wrap.appendChild(linksRow);
    downloadsDiv.appendChild(wrap);

    resultadosDiv.style.display = 'block';
}

function simularOrdenacaoLocal(csv, coluna, tipo, reverso, algoritmos) {
    const linhas = csv.split('\n');
    const cabecalho = linhas[0];
    const dados = linhas.slice(1).filter((l) => l.trim());

    const converter = (valor) => {
        if (tipo === 'int') return parseInt(valor, 10);
        if (tipo === 'float') return parseFloat(valor);
        return valor;
    };

    const ordenar = (dadosOrd, algoritmo) => {
        const sorted = [...dadosOrd];
        if (algoritmo === 'merge') {
            return mergeSort(sorted, coluna, converter, reverso);
        }
        return quickSort(sorted, coluna, converter, reverso);
    };

    const mergeSort = (arr, col, conv, rev) => {
        if (arr.length <= 1) return arr;
        const meio = Math.floor(arr.length / 2);
        const esquerda = mergeSort(arr.slice(0, meio), col, conv, rev);
        const direita = mergeSort(arr.slice(meio), col, conv, rev);
        return merge(esquerda, direita, col, conv, rev);
    };

    const merge = (esq, dir, col, conv, rev) => {
        const resultado = [];
        let i = 0;
        let j = 0;
        while (i < esq.length && j < dir.length) {
            const valEsq = conv(esq[i].split(',')[col]);
            const valDir = conv(dir[j].split(',')[col]);
            const cond = rev ? valEsq > valDir : valEsq < valDir;
            if (cond) {
                resultado.push(esq[i++]);
            } else {
                resultado.push(dir[j++]);
            }
        }
        return [...resultado, ...esq.slice(i), ...dir.slice(j)];
    };

    const quickSort = (arr, col, conv, rev) => {
        if (arr.length <= 1) return arr;
        const pivo = arr[0];
        const valPivo = conv(pivo.split(',')[col]);
        const menores = [];
        const maiores = [];
        for (let i = 1; i < arr.length; i++) {
            const valAtual = conv(arr[i].split(',')[col]);
            if (rev ? valAtual > valPivo : valAtual < valPivo) {
                menores.push(arr[i]);
            } else {
                maiores.push(arr[i]);
            }
        }
        return [
            ...quickSort(menores, col, conv, rev),
            pivo,
            ...quickSort(maiores, col, conv, rev),
        ];
    };

    const tempos = {};
    const arquivos = {};

    for (const alg of algoritmos) {
        const inicio = performance.now();
        const sorted = ordenar([...dados], alg);
        const fim = performance.now();
        tempos[alg] = (fim - inicio) / 1000;
        arquivos[alg] = [cabecalho, ...sorted].join('\n');
    }

    showToast('Sem conexão com o servidor: exibindo uma ordenação local aproximada.', 'default');
    mostrarResultados({ tempos, arquivos });
}
