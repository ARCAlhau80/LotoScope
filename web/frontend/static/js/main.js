/**
 * 🎯 LotoScope Web - JavaScript Principal (Versão Simplificada para Debug)
 */

console.log('📦 Carregando LotoScopeWeb...');

class LotoScopeWeb {
    constructor() {
        console.log('🏗️ Construindo LotoScopeWeb...');
        // 🎯 SISTEMA DE 4 ESTADOS POR NÚMERO
        this.selectedNumbers = [];     // 1º clique: Números para estratégia percentual (azul)
        this.mandatoryNumbers = [];    // 2º clique: Números obrigatórios em todas as combinações (dourado)
        this.excludedNumbers = [];     // 3º clique: Números excluídos (cinza + X)
        this.neutralNumbers = [];      // 4º clique: Volta ao normal
        
        // Compatibilidade com versão anterior
        this.fixedNumbers = [];        // DEPRECATED: usar selectedNumbers + mandatoryNumbers
        
        this.gameSize = 15;
        this.quantity = 1;
        this.apiBaseUrl = window.location.origin + '/api';
        this.riskProfile = 'moderado'; // Perfil padrão
        this.lastSequentialAnalysis = null; // Cache da última análise
        
        // Filtros dinâmicos aplicados pela análise sequencial
        this.dynamicFilters = {
            menor_que_ultimo: null,
            maior_que_ultimo: null, 
            igual_ao_ultimo: null,
            soma_total_min: null,
            soma_total_max: null
        };
        
        // 🎯 Controle de cliques para triple-click
        this.clickTimeouts = new Map(); // Armazena timeouts de clique por número
        this.clickCounts = new Map(); // Conta cliques por número
        
        console.log('🔧 Chamando init...');
        this.init();
    }

    init() {
        console.log('🚀 Inicializando LotoScope Web...');
        try {
            this.createNumbersGrid();
            console.log('✅ Grid criado');
            this.bindEvents();
            console.log('✅ Eventos vinculados');
            this.updateDisplay();
            console.log('✅ Display atualizado');
            this.checkApiHealth();
            console.log('✅ API verificada');
            this.loadContestInfo();
            console.log('✅ Informações do concurso carregadas');
        } catch (error) {
            console.error('❌ Erro no init:', error);
        }
    }

    createNumbersGrid() {
        const grid = document.getElementById('numbersGrid');
        if (!grid) {
            console.error('❌ Elemento numbersGrid não encontrado!');
            return;
        }
        
        grid.innerHTML = '';
        for (let i = 1; i <= 25; i++) {
            const button = document.createElement('button');
            button.className = 'number-btn';
            button.textContent = i;
            button.dataset.number = i;
            
            // 🎯 Triple-click handler: neutral → selected → excluded → neutral
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNumberClick(i);
            });
            
            grid.appendChild(button);
        }
        
        // 📝 Atualizar instruções do grid para incluir triple-click
        const gridInfo = document.querySelector('.grid-info');
        if (gridInfo) {
            gridInfo.innerHTML = `
                <div style="text-align: center; margin-top: 10px;">
                    <p><strong>Instruções:</strong></p>
                    <p>🔵 <strong>1º clique:</strong> Selecionar número (azul)</p>
                    <p>🔴 <strong>2º clique:</strong> Excluir número (vermelho - não aparecerá)</p>
                    <p>⚪ <strong>3º clique:</strong> Neutral (volta ao normal)</p>
                </div>
            `;
        }
        
        console.log('✅ Grid de números criado com 25 botões e sistema triple-click');
    }

    bindEvents() {
        // Game size selector
        const gameSize = document.getElementById('gameSize');
        if (gameSize) {
            gameSize.addEventListener('change', (e) => {
                this.gameSize = parseInt(e.target.value);
                this.updateDisplay();
                this.calculateProbability();
            });
        }

        // Quantity selector
        const quantity = document.getElementById('quantity');
        if (quantity) {
            quantity.addEventListener('change', (e) => {
                const value = e.target.value;
                // Permitir vazio, 0 ou números positivos
                if (value === "" || value === "0") {
                    this.quantity = null; // Indica "todas"
                } else {
                    this.quantity = parseInt(value) || 1;
                }
                this.updateDisplay();
                this.calculateProbability();
            });
        }

        // Risk Profile selector
        const riskProfile = document.getElementById('riskProfile');
        if (riskProfile) {
            riskProfile.addEventListener('change', async (e) => {
                this.riskProfile = e.target.value;
                console.log(`🎯 Perfil de risco alterado para: ${this.riskProfile}`);
                
                // Aplicar filtros imediatamente (modo teste)
                await this.applySequentialFilters(null, this.riskProfile);
            });
        }

        // Clear button
        const clearBtn = document.getElementById('clearSelection');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearSelection());
        }

        // Refresh Cache button
        const refreshCacheBtn = document.getElementById('refreshCacheBtn');
        if (refreshCacheBtn) {
            refreshCacheBtn.addEventListener('click', () => this.refreshCache());
        }

        // Generate button
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateCombinations());
        }
        
        // Export button
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportCombinations());
        }

        // Análise Sequencial button
        const analiseSequencialBtn = document.getElementById('analiseSequencialBtn');
        if (analiseSequencialBtn) {
            analiseSequencialBtn.addEventListener('click', () => this.showAnaliseSequencial());
        }

        // Modal close buttons
        const modalClose = document.querySelector('.modal-close');
        const modalOverlay = document.querySelector('.modal-overlay');
        const closeAnaliseModal = document.getElementById('closeAnaliseModal');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
        if (closeAnaliseModal) {
            closeAnaliseModal.addEventListener('click', () => this.closeModal());
        }
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    this.closeModal();
                }
            });
        }
        
        console.log('✅ Eventos vinculados');
    }

    handleNumberClick(number) {
        console.log(`🎯 Clique no número: ${number}`);
        
        // Determinar estado atual do número (4 estados)
        let currentState = this.getNumberState(number);
        
        // Aplicar transição de estado: neutral → selected → mandatory → excluded → neutral
        let newState;
        switch (currentState) {
            case 'neutral':
                newState = 'selected';
                break;
            case 'selected':
                newState = 'mandatory';
                break;
            case 'mandatory':
                newState = 'excluded';
                break;
            case 'excluded':
                newState = 'neutral';
                break;
        }
        
        console.log(`🔄 ${number}: ${currentState} → ${newState}`);
        
        // Aplicar novo estado
        this.setNumberState(number, newState);
        
        // Atualizar display e probabilidade
        this.updateDisplay();
        this.calculateProbability();
    }

    getNumberState(number) {
        if (this.selectedNumbers.includes(number)) {
            return 'selected';
        } else if (this.mandatoryNumbers.includes(number)) {
            return 'mandatory';
        } else if (this.excludedNumbers.includes(number)) {
            return 'excluded';
        } else {
            return 'neutral';
        }
    }

    setNumberState(number, state) {
        const button = document.querySelector(`[data-number="${number}"]`);
        if (!button) return;
        
        // Remover de todas as listas primeiro
        this.selectedNumbers = this.selectedNumbers.filter(n => n !== number);
        this.mandatoryNumbers = this.mandatoryNumbers.filter(n => n !== number);
        this.excludedNumbers = this.excludedNumbers.filter(n => n !== number);
        this.fixedNumbers = this.fixedNumbers.filter(n => n !== number); // Manter compatibilidade
        
        // Remover todas as classes de estado
        button.classList.remove('selected', 'mandatory', 'excluded');
        
        // Aplicar novo estado
        switch (state) {
            case 'selected':
                // Verificar limite total de números (selected + mandatory)
                const totalSelected = this.selectedNumbers.length + this.mandatoryNumbers.length;
                if (totalSelected >= 25) {
                    this.showStatus('⚠️ Máximo de 25 números entre selecionados e obrigatórios', 'warning');
                    return;
                }
                this.selectedNumbers.push(number);
                this.selectedNumbers.sort((a, b) => a - b);
                this.fixedNumbers.push(number); // Manter compatibilidade
                this.fixedNumbers.sort((a, b) => a - b);
                button.classList.add('selected');
                this.showStatus(`🔵 Número ${number} selecionado para estratégia percentual`, 'info');
                break;
                
            case 'mandatory':
                // Verificar limite total de números (selected + mandatory)
                const totalMandatory = this.selectedNumbers.length + this.mandatoryNumbers.length;
                if (totalMandatory >= 25) {
                    this.showStatus('⚠️ Máximo de 25 números entre selecionados e obrigatórios', 'warning');
                    return;
                }
                this.mandatoryNumbers.push(number);
                this.mandatoryNumbers.sort((a, b) => a - b);
                this.fixedNumbers.push(number); // Manter compatibilidade
                this.fixedNumbers.sort((a, b) => a - b);
                button.classList.add('mandatory');
                this.showStatus(`🟡 Número ${number} obrigatório (aparece em todas as combinações)`, 'info');
                break;
                
            case 'excluded':
                this.excludedNumbers.push(number);
                this.excludedNumbers.sort((a, b) => a - b);
                button.classList.add('excluded');
                this.showStatus(`🔴 Número ${number} excluído`, 'warning');
                break;
                
            case 'neutral':
                // Já removido das listas acima
                this.showStatus(`⚪ Número ${number} neutro`, 'info');
                break;
        }
        
        console.log(`✅ Estado aplicado:`);
        console.log(`   Selecionados: [${this.selectedNumbers}]`);
        console.log(`   Obrigatórios: [${this.mandatoryNumbers}]`);
        console.log(`   Excluídos: [${this.excludedNumbers}]`);
    }

    // 🗑️ Manter método legacy para compatibilidade (não usado mais)
    toggleNumber(number) {
        console.log(`🔄 toggleNumber legacy chamado para: ${number} - redirecionando para handleNumberClick`);
        this.handleNumberClick(number);
    }

    clearSelection() {
        console.log('🧹 Limpando seleção (4 estados)');
        this.selectedNumbers = [];
        this.mandatoryNumbers = [];
        this.excludedNumbers = [];
        this.fixedNumbers = []; // Manter compatibilidade
        
        document.querySelectorAll('.number-btn').forEach(btn => {
            btn.classList.remove('selected', 'mandatory', 'excluded');
        });
        
        this.updateDisplay();
        this.calculateProbability();
        this.showStatus('🧹 Seleção limpa (todos os números neutros)', 'success');
    }

    async refreshCache() {
        console.log('🔄 Limpando cache e atualizando análise...');
        
        try {
            this.showStatus('🔄 Atualizando análise...', 'info');
            
            const response = await fetch(`${this.apiBaseUrl}/clear-cache`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Cache limpo:', data);
                
                // Recarregar informações do concurso
                await this.loadContestInfo();
                
                // Recalcular probabilidade
                await this.calculateProbability();
                
                this.showStatus('✅ Análise atualizada com dados mais recentes!', 'success');
            } else {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao atualizar cache:', error);
            this.showStatus('❌ Erro ao atualizar análise', 'error');
        }
    }

    updateDisplay() {
        // Atualizar contagem de números (4 estados)
        const fixedCount = document.getElementById('fixedCount');
        const fixedNumbers = document.getElementById('fixedNumbers');
        
        const totalNumbers = this.selectedNumbers.length + this.mandatoryNumbers.length;
        
        if (fixedCount) {
            if (totalNumbers === 0) {
                fixedCount.textContent = `0 números`;
            } else {
                let description = [];
                if (this.selectedNumbers.length > 0) {
                    description.push(`${this.selectedNumbers.length} selecionados`);
                }
                if (this.mandatoryNumbers.length > 0) {
                    description.push(`${this.mandatoryNumbers.length} obrigatórios`);
                }
                fixedCount.textContent = `${totalNumbers} números (${description.join(' + ')})`;
            }
        }
        
        if (fixedNumbers) {
            if (totalNumbers === 0) {
                fixedNumbers.innerHTML = '<em>Nenhum número selecionado</em>';
            } else {
                let html = [];
                
                // Mostrar números selecionados (azul)
                if (this.selectedNumbers.length > 0) {
                    html.push('<strong>Selecionados:</strong> ');
                    html.push(this.selectedNumbers.map(n => 
                        `<span class="selected-number">${n}</span>`
                    ).join(''));
                }
                
                // Mostrar números obrigatórios (dourado)
                if (this.mandatoryNumbers.length > 0) {
                    if (html.length > 0) html.push('<br>');
                    html.push('<strong>Obrigatórios:</strong> ');
                    html.push(this.mandatoryNumbers.map(n => 
                        `<span class="mandatory-number">${n}</span>`
                    ).join(''));
                }
                
                fixedNumbers.innerHTML = html.join('');
            }
        }
        
        // 🚫 Mostrar números excluídos
        const excludedCount = document.getElementById('excludedCount');
        const excludedNumbers = document.getElementById('excludedNumbers');
        
        if (excludedCount) {
            excludedCount.textContent = `${this.excludedNumbers.length} números`;
        }
        
        if (excludedNumbers) {
            if (this.excludedNumbers.length === 0) {
                excludedNumbers.innerHTML = '<em>Nenhum número excluído</em>';
            } else {
                excludedNumbers.innerHTML = this.excludedNumbers.map(n => 
                    `<span class="excluded-number">${n}</span>`
                ).join('');
            }
        }
        
        // Manter fixedNumbers compatível
        this.fixedNumbers = [...this.selectedNumbers, ...this.mandatoryNumbers].sort((a, b) => a - b);
        
        const remainingSlots = this.gameSize - totalNumbers;
        
        // Atualizar botão de gerar
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            // Nova lógica: permitir geração se há números selecionados (estratégia inteligente ativa)
            const canGenerate = totalNumbers <= 25;
            
            if (canGenerate && totalNumbers > 0) {
                generateBtn.disabled = false;
                
                // Texto do botão baseado na estratégia
                if (this.mandatoryNumbers.length > 0 && this.selectedNumbers.length > 0) {
                    // Estratégia mista: obrigatórios + selecionados
                    if (this.quantity === null || this.quantity === 0) {
                        generateBtn.innerHTML = `<i class="fas fa-brain"></i> Gerar TODAS (${this.mandatoryNumbers.length} obrig. + ${this.selectedNumbers.length} selecc.)`;
                    } else {
                        generateBtn.innerHTML = `<i class="fas fa-brain"></i> Gerar ${this.quantity} (${this.mandatoryNumbers.length} obrig. + ${this.selectedNumbers.length} selecc.)`;
                    }
                } else if (this.mandatoryNumbers.length > 0) {
                    // Apenas obrigatórios
                    if (this.quantity === null || this.quantity === 0) {
                        generateBtn.innerHTML = `<i class="fas fa-magic"></i> Gerar TODAS (${this.mandatoryNumbers.length} obrigatórios)`;
                    } else {
                        generateBtn.innerHTML = `<i class="fas fa-magic"></i> Gerar ${this.quantity} (${this.mandatoryNumbers.length} obrigatórios)`;
                    }
                } else {
                    // Apenas selecionados (estratégia percentual)
                    if (this.quantity === null || this.quantity === 0) {
                        generateBtn.innerHTML = `<i class="fas fa-brain"></i> Gerar TODAS (${this.selectedNumbers.length} selecionados)`;
                    } else {
                        generateBtn.innerHTML = `<i class="fas fa-brain"></i> Gerar ${this.quantity} (${this.selectedNumbers.length} selecionados)`;
                    }
                }
            } else if (totalNumbers === 0) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-magic"></i> Gerar Combinações Aleatórias';
            } else {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Muitos números selecionados (máx. 25)';
            }
        }
    }

    async calculateProbability() {
        console.log('📊 Calculando probabilidade (4 estados)...');
        try {
            const response = await fetch(`${this.apiBaseUrl}/calculate-probability`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    // Novo sistema de 4 estados
                    selected_numbers: this.selectedNumbers,
                    mandatory_numbers: this.mandatoryNumbers,
                    excluded_numbers: this.excludedNumbers,
                    
                    // Compatibilidade com sistema antigo
                    fixed_numbers: this.fixedNumbers,
                    
                    game_size: this.gameSize,
                    quantity: this.quantity === null ? "" : this.quantity,
                    dynamic_filters: this.dynamicFilters,
                    risk_profile: this.riskProfile
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Probabilidade calculada:', data);
                this.displayProbability(data);
            }
        } catch (error) {
            console.error('❌ Erro ao calcular probabilidade:', error);
        }
    }

    async generateCombinations() {
        console.log('🎲 Gerando combinações...');
        
        // Mostrar loading
        const loadingSpinner = document.getElementById('loadingSpinner');
        const resultsSection = document.getElementById('resultsSection');
        
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        
        try {
            // Preparar dados para envio usando o novo sistema de 4 estados
            const requestData = {
                // Manter compatibilidade com o sistema antigo
                fixed_numbers: this.fixedNumbers,
                
                // Novo sistema de 4 estados
                selected_numbers: this.selectedNumbers,
                mandatory_numbers: this.mandatoryNumbers,
                excluded_numbers: this.excludedNumbers,
                
                game_size: this.gameSize,
                quantity: this.quantity === null ? "" : this.quantity,
                risk_profile: this.riskProfile
            };
            
            // Adicionar filtros dinâmicos se existirem
            if (Object.values(this.dynamicFilters).some(filter => filter !== null)) {
                // Para CONSERVADOR: enviar apenas os 3 filtros principais
                if (this.riskProfile === 'conservador') {
                    requestData.dynamic_filters = {
                        menor_que_ultimo: this.dynamicFilters.menor_que_ultimo,
                        maior_que_ultimo: this.dynamicFilters.maior_que_ultimo,
                        igual_ao_ultimo: this.dynamicFilters.igual_ao_ultimo
                    };
                    console.log('🛡️ CONSERVADOR: Enviando apenas 3 filtros dinâmicos principais');
                } else {
                    // Para AGRESSIVO e MODERADO: enviar todos os filtros
                    requestData.dynamic_filters = this.dynamicFilters;
                }
                console.log('📊 Enviando filtros dinâmicos:', this.dynamicFilters);
            }

            console.log('📤 Dados enviados (4 estados):');
            console.log('  Selecionados:', this.selectedNumbers);
            console.log('  Obrigatórios:', this.mandatoryNumbers);
            console.log('  Excluídos:', this.excludedNumbers);
            console.log('  Fixos (compat.):', this.fixedNumbers);

            const response = await fetch(`${this.apiBaseUrl}/generate-combinations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Combinações geradas:', data);
                this.displayCombinations(data);
                
                // Mostrar status com informações detalhadas do 4-state system
                let statusMsg = `✅ ${data.count} combinação${data.count > 1 ? 'ões' : ''} gerada${data.count > 1 ? 's' : ''}!`;
                
                let details = [];
                if (this.mandatoryNumbers.length > 0) {
                    details.push(`${this.mandatoryNumbers.length} obrigatórios`);
                }
                if (this.selectedNumbers.length > 0) {
                    details.push(`${this.selectedNumbers.length} selecionados`);
                }
                if (this.excludedNumbers.length > 0) {
                    details.push(`${this.excludedNumbers.length} excluídos`);
                }
                
                if (details.length > 0) {
                    statusMsg += ` (${details.join(', ')})`;
                }
                
                this.showStatus(statusMsg, 'success');
            } else {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao gerar combinações:', error);
            this.showStatus('❌ Erro ao gerar combinações', 'error');
            
            // Esconder loading em caso de erro
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
        }
    }

    displayProbability(data) {
        const totalCombinations = document.getElementById('totalCombinations');
        const probability = document.getElementById('probability');
        
        if (totalCombinations) {
            totalCombinations.textContent = data.total_combinations.toLocaleString();
        }
        
        if (probability) {
            probability.textContent = data.probability;
        }
    }

    displayCombinations(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContainer = document.getElementById('resultsContainer');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const exportBtn = document.getElementById('exportBtn');
        
        // Salvar combinações para exportação
        this.lastCombinations = data.combinations;
        
        // Esconder loading
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        // Mostrar seção de resultados
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // Mostrar botão de exportação
        if (exportBtn && data.combinations.length > 0) {
            exportBtn.style.display = 'inline-block';
        }
        
        if (!resultsContainer) return;
        
        let html = `
            <div class="combinations-header">
                <h4><i class="fas fa-trophy"></i> ${data.count} Combinação${data.count > 1 ? 'ões' : ''} Gerada${data.count > 1 ? 's' : ''}</h4>
            </div>
            <div class="combinations-list">
        `;
        
        data.combinations.forEach((combo, index) => {
            html += `
                <div class="combination-item">
                    <div class="combination-number">#${index + 1}</div>
                    <div class="combination-numbers">
                        ${combo.map(num => `<span class="number-badge">${num}</span>`).join('')}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('statusMessage');
        if (statusDiv) {
            statusDiv.textContent = message;
            statusDiv.className = `status-message ${type}`;
        }
        console.log(`📢 Status: ${message}`);
    }

    async checkApiHealth() {
        console.log('🔍 Verificando API health...');
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                const data = await response.json();
                console.log('✅ API funcionando:', data);
                this.showStatus('✅ Conectado ao servidor', 'success');
            }
        } catch (error) {
            console.error('❌ Erro na API:', error);
            this.showStatus('⚠️ Servidor offline', 'warning');
        }
    }

    async loadContestInfo() {
        console.log('📊 Carregando informações do concurso...');
        try {
            const response = await fetch(`${this.apiBaseUrl}/trend-info`);
            if (response.ok) {
                const data = await response.json();
                this.displayContestInfo(data.contest_info, data.trend_info);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar info do concurso:', error);
        }
    }

    displayContestInfo(contestInfo, trendInfo) {
        const nextContest = document.getElementById('nextContest');
        const lastContest = document.getElementById('lastContest');
        const currentTrend = document.getElementById('currentTrend');

        if (nextContest) {
            nextContest.textContent = contestInfo?.proximo_concurso || 'N/A';
        }

        if (lastContest) {
            lastContest.textContent = contestInfo?.ultimo_concurso || 'N/A';
        }

        if (currentTrend) {
            currentTrend.textContent = trendInfo?.resumo || 'N/A';
        }

        // Carregar números do último sorteio
        this.loadLastDrawNumbers();
    }

    async loadLastDrawNumbers() {
        try {
            console.log('🔍 Carregando números do último sorteio...');
            const response = await fetch(`${this.apiBaseUrl}/last-draw`);
            console.log('📡 Response status:', response.status);
            
            const data = await response.json();
            console.log('📊 Dados recebidos:', data);

            const currentNumbers = document.getElementById('currentNumbers');
            if (currentNumbers && data.success) {
                console.log('✅ Elemento encontrado, criando números...');
                currentNumbers.innerHTML = '';
                
                data.numbers.forEach(number => {
                    const numberElement = document.createElement('span');
                    numberElement.className = 'current-number';
                    numberElement.textContent = number.toString().padStart(2, '0');
                    currentNumbers.appendChild(numberElement);
                });
                console.log('✅ Números do sorteio exibidos com sucesso');
            } else if (currentNumbers) {
                console.log('❌ Erro nos dados ou elemento não encontrado');
                currentNumbers.textContent = 'Erro ao carregar números';
            }
        } catch (error) {
            console.error('❌ Erro ao carregar números do último sorteio:', error);
            const currentNumbers = document.getElementById('currentNumbers');
            if (currentNumbers) {
                currentNumbers.textContent = 'Erro ao carregar';
            }
        }
    }

    async exportCombinations() {
        console.log('📤 Exportando combinações...');
        
        if (!this.lastCombinations || this.lastCombinations.length === 0) {
            this.showStatus('⚠️ Nenhuma combinação para exportar', 'warning');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/export-combinations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    combinations: this.lastCombinations
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.downloadFile(data.content, data.filename);
                this.showStatus('✅ Arquivo exportado com sucesso!', 'success');
            } else {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao exportar:', error);
            this.showStatus('❌ Erro ao exportar combinações', 'error');
        }
    }

    downloadFile(content, filename) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    async showAnaliseSequencial() {
        console.log('📊 Iniciando análise sequencial...');
        
        // Mostrar modal
        const modal = document.getElementById('analiseSequencialModal');
        if (!modal) {
            this.showStatus('❌ Modal de análise não encontrado', 'error');
            return;
        }

        modal.style.display = 'block';
        
        // Mostrar loading
        const modalContent = document.getElementById('analiseSequencialContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Analisando padrões sequenciais...</p>
                </div>
            `;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/analise-sequencial`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });

            if (response.ok) {
                const data = await response.json();
                this.displayAnaliseResults(data);
            } else {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro na análise sequencial:', error);
            if (modalContent) {
                modalContent.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>Erro na Análise</h3>
                        <p>Não foi possível realizar a análise sequencial.</p>
                        <p class="error-details">${error.message}</p>
                    </div>
                `;
            }
        }
    }

    displayAnaliseResults(data) {
        const modalContent = document.getElementById('analiseSequencialContent');
        if (!modalContent) return;

        let html = `
            <div class="analise-results">
                <h3><i class="fas fa-chart-line"></i> Análise Sequencial Completa</h3>
                <div class="analise-summary">
                    <p><strong>Último jogo analisado:</strong> ${data.ultimo_jogo || 'N/A'}</p>
                    <p><strong>Total de padrões analisados:</strong> ${data.total_padroes || 0}</p>
                </div>
        `;

        // Análise por categoria
        if (data.analise_menor_que) {
            html += this.formatAnaliseSection('Menor que Último', data.analise_menor_que, 'chart-bar');
        }

        if (data.analise_maior_que) {
            html += this.formatAnaliseSection('Maior que Último', data.analise_maior_que, 'chart-line');
        }

        if (data.analise_igual_ao) {
            html += this.formatAnaliseSection('Igual ao Último', data.analise_igual_ao, 'equals');
        }

        html += `
                <div class="analise-actions">
                    <h4><i class="fas fa-magic"></i> Aplicar Filtros Automaticamente</h4>
                    <div class="action-buttons">
                        <button class="btn-apply-profile" data-profile="conservador">
                            🛡️ Aplicar Conservador
                        </button>
                        <button class="btn-apply-profile" data-profile="moderado">
                            📊 Aplicar Moderado
                        </button>
                        <button class="btn-apply-profile" data-profile="agressivo">
                            🎯 Aplicar Agressivo
                        </button>
                    </div>
                    <p class="action-description">
                        Os filtros serão aplicados automaticamente baseados na análise sequencial
                    </p>
                </div>
                <div class="analise-footer">
                    <p class="disclaimer">
                        <i class="fas fa-info-circle"></i>
                        Análise baseada em padrões históricos. Os resultados não garantem acertos futuros.
                    </p>
                </div>
            </div>
        `;

        modalContent.innerHTML = html;
        
        // Cachear dados da análise
        this.lastSequentialAnalysis = data;
        
        // Adicionar event listeners para os botões de aplicar perfil
        const profileButtons = modalContent.querySelectorAll('.btn-apply-profile');
        profileButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const profile = e.target.getAttribute('data-profile');
                await this.applySequentialFilters(data, profile);
                
                // Atualizar seletor de perfil na interface
                const riskProfileSelect = document.getElementById('riskProfile');
                if (riskProfileSelect) {
                    riskProfileSelect.value = profile;
                    this.riskProfile = profile;
                }
                
                // Fechar modal após aplicar
                setTimeout(() => {
                    this.closeModal();
                }, 1500);
            });
        });
    }

    formatAnaliseSection(titulo, analise, icon) {
        if (!analise || !analise.predicoes_proximas) return '';

        let html = `
            <div class="analise-section">
                <h4><i class="fas fa-${icon}"></i> ${titulo}</h4>
                <div class="analise-details">
                    <div class="current-value">
                        <span class="label">Valor Atual:</span>
                        <span class="value">${analise.valor_atual || 'N/A'}</span>
                    </div>
                    <div class="prediction-confidence">
                        <span class="label">Confiança:</span>
                        <span class="value">${analise.confianca || 'N/A'}%</span>
                    </div>
                </div>
                <div class="predictions">
                    <h5>Próximas Predições:</h5>
                    <div class="prediction-grid">
        `;

        // Adicionar predições
        analise.predicoes_proximas.forEach(pred => {
            const probabilidade = (pred.probabilidade * 100).toFixed(1);
            html += `
                <div class="prediction-item">
                    <div class="pred-value">${pred.valor}</div>
                    <div class="pred-prob">${probabilidade}%</div>
                    <div class="pred-count">${pred.ocorrencias} vezes</div>
                </div>
            `;
        });

        html += `
                    </div>
                </div>
        `;
        
        // Adicionar seção de perfis de risco se disponível
        if (analise.perfis_risco) {
            html += `
                <div class="perfis-risco">
                    <h5>Perfis de Aplicação:</h5>
                    <div class="perfis-grid">
                        <div class="perfil-item conservador">
                            <strong>🛡️ Conservador:</strong> ${analise.perfis_risco.conservador.min} - ${analise.perfis_risco.conservador.max}
                        </div>
                        <div class="perfil-item moderado">
                            <strong>📊 Moderado:</strong> ${analise.perfis_risco.moderado.min} - ${analise.perfis_risco.moderado.max}
                        </div>
                        <div class="perfil-item agressivo">
                            <strong>🎯 Agressivo:</strong> ${analise.perfis_risco.agressivo.min} - ${analise.perfis_risco.agressivo.max}
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += `
            </div>
        `;

        return html;
    }

    closeModal() {
        const modal = document.getElementById('analiseSequencialModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async applySequentialFilters(data = null, profile = null) {
        console.log('🎯 Aplicando filtros automáticos baseados na análise sequencial...');
        
        const selectedProfile = profile || this.riskProfile;
        console.log(`📊 Usando perfil: ${selectedProfile}`);
        
        // Se não há dados da análise sequencial, usar filtros baseados em inversão de tendências
        if (!data || !data.previsoes) {
            console.log('🔄 Usando filtros baseados em inversão de tendências');
            await this.applyTrendBasedFilters(selectedProfile);
            return;
        }

        // Código original para quando a análise sequencial funcionar
        Object.keys(data.previsoes).forEach(campo => {
            const previsao = data.previsoes[campo];
            const perfil = previsao.perfis_risco[selectedProfile];
            
            if (perfil) {
                console.log(`🔧 ${campo}: ${perfil.min} - ${perfil.max} (${selectedProfile})`);
                
                switch(campo) {
                    case 'menor_que_ultimo':
                        this.updateFilterValue('menorQueUltimo', perfil.min, perfil.max);
                        break;
                    case 'maior_que_ultimo':
                        this.updateFilterValue('maiorQueUltimo', perfil.min, perfil.max);
                        break;
                    case 'igual_ao_ultimo':
                        this.updateFilterValue('igualAoUltimo', perfil.min, perfil.max);
                        break;
                }
            }
        });

        // Mostrar status de aplicação
        const profileNames = {
            'conservador': '🛡️ Conservador',
            'moderado': '📊 Moderado', 
            'agressivo': '🎯 Agressivo'
        };
        
        this.showStatus(`✅ Filtros aplicados - Perfil ${profileNames[selectedProfile]}`, 'success');
        
        // Recalcular probabilidades
        this.calculateProbability();
    }

    async applyTrendBasedFilters(profile) {
        console.log(`🔄 Aplicando filtros baseados em inversão de tendências REAIS: ${profile}`);
        
        try {
            // Obter APENAS dados reais do último concurso via API
            const ultimaConcursoData = await this.getUltimoConcursoData();
            
            // Aplicar lógica de inversão baseada na tendência atual REAL
            this.applyInversionLogic(ultimaConcursoData, profile);
            
            console.log('🔧 ✅ Filtros de inversão REAIS aplicados:', this.dynamicFilters);
            
        } catch (error) {
            console.error('❌ ERRO: Não foi possível aplicar filtros baseados em dados reais:', error);
            
            // Limpar filtros dinâmicos para usar filtros padrão do sistema
            this.dynamicFilters = {
                menor_que_ultimo: null,
                maior_que_ultimo: null,
                igual_ao_ultimo: null,
                soma_total_min: null,
                soma_total_max: null
            };
            
            // Notificar usuário do problema
            this.showStatus('⚠️ Dados reais indisponíveis - usando filtros padrão', 'warning');
            console.log('⚠️ Usando filtros padrão do sistema (sem inversão de tendências)');
        }
    }
    
    async getUltimoConcursoData() {
        try {
            console.log('🔍 Buscando dados REAIS do último concurso...');
            const response = await fetch(`${this.apiBaseUrl}/trend-info`);
            
            if (response.ok) {
                const data = await response.json();
                
                // APENAS dados reais - sem fallback simulado
                if (data.trend_info && data.trend_info.ultimo_concurso_real) {
                    console.log('📊 ✅ Dados REAIS obtidos do último concurso:', data.trend_info.ultimo_concurso_real);
                    
                    // Extrair valores reais do último concurso
                    const realData = {
                        menor_que_ultimo: data.trend_info.ultimo_concurso_real.menor_que_ultimo,
                        maior_que_ultimo: data.trend_info.ultimo_concurso_real.maior_que_ultimo,
                        igual_ao_ultimo: data.trend_info.ultimo_concurso_real.igual_ao_ultimo,
                        soma_total: data.trend_info.ultimo_concurso_real.soma_total,
                        concurso: data.trend_info.ultimo_concurso_real.concurso
                    };
                    
                    // Validar se todos os dados essenciais estão presentes
                    if (realData.menor_que_ultimo !== null && realData.menor_que_ultimo !== undefined && 
                        realData.maior_que_ultimo !== null && realData.maior_que_ultimo !== undefined && 
                        realData.igual_ao_ultimo !== null && realData.igual_ao_ultimo !== undefined && 
                        realData.soma_total !== null && realData.soma_total !== undefined &&
                        realData.concurso !== null && realData.concurso !== undefined) {
                        
                        console.log(`✅ Dados REAIS completos do concurso ${realData.concurso}:`, realData);
                        return realData;
                    } else {
                        console.error('❌ Dados REAIS incompletos:', realData);
                        throw new Error('Dados reais do último concurso incompletos');
                    }
                } else {
                    console.error('❌ Nenhum dado de tendência disponível');
                    throw new Error('Dados de tendência não disponíveis');
                }
            } else {
                console.error('❌ Erro na resposta da API:', response.status);
                throw new Error(`API retornou status ${response.status}`);
            }
        } catch (error) {
            console.error('❌ ERRO: Não foi possível obter dados reais:', error);
            throw error;
        }
    }
    
    applyInversionLogic(ultimoConcurso, profile) {
        console.log(`📊 Dados REAIS do concurso ${ultimoConcurso.concurso}:`, ultimoConcurso);
        console.log(`🎯 APLICANDO NOVA LÓGICA DE TENDÊNCIAS - Perfil: ${profile}`);
        
        // NOVA LÓGICA DE INVERSÃO MATEMÁTICA BASEADA EM PERFIS DE RISCO:
        // AGRESSIVO: Inversão radical - valores altos → próximo baixo, valores baixos → próximo alto
        // MODERADO: Inversão média - range amplo com tendência oposta moderada
        // CONSERVADOR: Usa EXATAMENTE os mesmos valores do MODERADO nos filtros dinâmicos
        
        const valorAtualMenor = ultimoConcurso.menor_que_ultimo;
        const valorAtualMaior = ultimoConcurso.maior_que_ultimo;
        
        // 1. MENOR_QUE_ULTIMO - Inversão baseada no valor atual
        console.log(`📈 menor_que_ultimo atual: ${valorAtualMenor}`);
        
        switch(profile) {
            case 'agressivo':
                // AGRESSIVO: Inversão total matemática
                if (valorAtualMenor <= 7) {
                    // Se atual é baixo → próximo terá MUITOS menores (12-15)
                    this.updateFilterValue('menorQueUltimo', 12, 15);
                    console.log(`🔥 AGRESSIVO: menor=${valorAtualMenor} (baixo) → inversão total (12-15)`);
                } else {
                    // Se atual é alto → próximo terá POUCOS menores (0-2)
                    this.updateFilterValue('menorQueUltimo', 0, 2);
                    console.log(`🔥 AGRESSIVO: menor=${valorAtualMenor} (alto) → inversão total (0-2)`);
                }
                break;
                
            case 'moderado':
                // MODERADO: Inversão matemática específica - ranges menores
                if (valorAtualMenor <= 7) {
                    // Se atual é baixo → próximo terá mais menores (11-15)
                    this.updateFilterValue('menorQueUltimo', 11, 15);
                    console.log(`⚖️ MODERADO: menor=${valorAtualMenor} (baixo) → próximo (11-15)`);
                } else {
                    // Se atual é alto → próximo terá menos menores (0 até metade-2, máximo 4)
                    const maxMenor = Math.min(4, Math.max(2, Math.floor(valorAtualMenor / 2) - 2));
                    this.updateFilterValue('menorQueUltimo', 0, maxMenor);
                    console.log(`⚖️ MODERADO: menor=${valorAtualMenor} (alto) → próximo (0-${maxMenor})`);
                }
                break;
                
            case 'conservador':
                // CONSERVADOR: Usa EXATAMENTE a mesma lógica matemática do MODERADO
                if (valorAtualMenor <= 7) {
                    // Se atual é baixo → próximo terá mais menores (11-15)
                    this.updateFilterValue('menorQueUltimo', 11, 15);
                    console.log(`🛡️ CONSERVADOR: menor=${valorAtualMenor} (baixo) → próximo (11-15) [IGUAL MODERADO]`);
                } else {
                    // Se atual é alto → próximo terá menos menores (0 até metade-2, máximo 4)
                    const maxMenor = Math.min(4, Math.max(2, Math.floor(valorAtualMenor / 2) - 2));
                    this.updateFilterValue('menorQueUltimo', 0, maxMenor);
                    console.log(`🛡️ CONSERVADOR: menor=${valorAtualMenor} (alto) → próximo (0-${maxMenor}) [IGUAL MODERADO]`);
                }
                break;
        }
        
        // 2. MAIOR_QUE_ULTIMO - Inversão baseada no valor atual
        console.log(`📊 maior_que_ultimo atual: ${valorAtualMaior}`);
        
        switch(profile) {
            case 'agressivo':
                // AGRESSIVO: Inversão total matemática
                if (valorAtualMaior <= 7) {
                    // Se atual é baixo → próximo terá MUITOS maiores (12-15)
                    this.updateFilterValue('maiorQueUltimo', 12, 15);
                    console.log(`🔥 AGRESSIVO: maior=${valorAtualMaior} (baixo) → inversão total (12-15)`);
                } else {
                    // Se atual é alto → próximo terá POUCOS maiores (0-2)
                    this.updateFilterValue('maiorQueUltimo', 0, 2);
                    console.log(`🔥 AGRESSIVO: maior=${valorAtualMaior} (alto) → inversão total (0-2)`);
                }
                break;
                
            case 'moderado':
                // MODERADO: Inversão matemática específica - ranges menores
                if (valorAtualMaior <= 7) {
                    // Se atual é baixo → próximo terá mais maiores (11-15)
                    this.updateFilterValue('maiorQueUltimo', 11, 15);
                    console.log(`⚖️ MODERADO: maior=${valorAtualMaior} (baixo) → próximo (11-15)`);
                } else {
                    // Se atual é alto → próximo terá menos maiores (0 até metade-2, máximo 4)
                    const maxMaior = Math.min(4, Math.max(2, Math.floor(valorAtualMaior / 2) - 2));
                    this.updateFilterValue('maiorQueUltimo', 0, maxMaior);
                    console.log(`⚖️ MODERADO: maior=${valorAtualMaior} (alto) → próximo (0-${maxMaior})`);
                }
                break;
                
            case 'conservador':
                // CONSERVADOR: Usa EXATAMENTE a mesma lógica matemática do MODERADO
                if (valorAtualMaior <= 7) {
                    // Se atual é baixo → próximo terá mais maiores (11-15)
                    this.updateFilterValue('maiorQueUltimo', 11, 15);
                    console.log(`🛡️ CONSERVADOR: maior=${valorAtualMaior} (baixo) → próximo (11-15) [IGUAL MODERADO]`);
                } else {
                    // Se atual é alto → próximo terá menos maiores (0 até metade-2, máximo 4)
                    const maxMaior = Math.min(4, Math.max(2, Math.floor(valorAtualMaior / 2) - 2));
                    this.updateFilterValue('maiorQueUltimo', 0, maxMaior);
                    console.log(`🛡️ CONSERVADOR: maior=${valorAtualMaior} (alto) → próximo (0-${maxMaior}) [IGUAL MODERADO]`);
                }
                break;
        }
        
        // 3. IGUAL_AO_ULTIMO - Inversão baseada no valor atual
        const valorAtualIgual = ultimoConcurso.igual_ao_ultimo;
        console.log(`📊 igual_ao_ultimo atual: ${valorAtualIgual}`);
        
        switch(profile) {
            case 'agressivo':
                // AGRESSIVO: Inversão radical para IGUAL_AO_ULTIMO
                if (valorAtualIgual <= 2) {
                    // Se atual é baixo → próximo terá MUITOS iguais (4-6)
                    this.updateFilterValue('igualAoUltimo', 4, 6);
                    console.log(`🔥 AGRESSIVO: ${valorAtualIgual} (baixo) → MUITOS iguais (4-6)`);
                } else {
                    // Se atual é alto → próximo terá POUCOS iguais (0-2)
                    this.updateFilterValue('igualAoUltimo', 0, 2);
                    console.log(`🔥 AGRESSIVO: ${valorAtualIgual} (alto) → POUCOS iguais (0-2)`);
                }
                break;
                
            case 'moderado':
                // MODERADO: Inversão dinâmica baseada no valor atual
                if (valorAtualIgual <= 3) {
                    // Se atual é baixo → próximo terá MUITOS iguais (4-6)
                    this.updateFilterValue('igualAoUltimo', 4, 6);
                    console.log(`⚖️ MODERADO: ${valorAtualIgual} (baixo) → MUITOS iguais (4-6)`);
                } else {
                    // Se atual é alto → próximo terá POUCOS iguais (0-2)
                    this.updateFilterValue('igualAoUltimo', 0, 2);
                    console.log(`⚖️ MODERADO: ${valorAtualIgual} (alto) → POUCOS iguais (0-2)`);
                }
                break;
                
            case 'conservador':
                // CONSERVADOR: Usa EXATAMENTE os mesmos valores do MODERADO
                if (valorAtualIgual <= 3) {
                    // Se atual é baixo → próximo terá MUITOS iguais (4-6)
                    this.updateFilterValue('igualAoUltimo', 4, 6);
                    console.log(`🛡️ CONSERVADOR: ${valorAtualIgual} (baixo) → MUITOS iguais (4-6) [IGUAL MODERADO]`);
                } else {
                    // Se atual é alto → próximo terá POUCOS iguais (0-2)
                    this.updateFilterValue('igualAoUltimo', 0, 2);
                    console.log(`🛡️ CONSERVADOR: ${valorAtualIgual} (alto) → POUCOS iguais (0-2) [IGUAL MODERADO]`);
                }
                break;
        }
        
        // 4. SOMA_TOTAL - Aplicar regras de faixa baseadas no perfil
        this.applySomaTotalRules(ultimoConcurso.soma_total, profile);
    }
    
    applySomaTotalRules(somaAtual, profile) {
        // Base: Análise sugere faixa em torno da soma atual
        const baseMin = somaAtual - 20;  // Faixa base moderada
        const baseMax = somaAtual + 20;
        
        switch(profile) {
            case 'agressivo':
                // Faixa menor: -10 do min, +10 do max (reduz faixa)
                this.dynamicFilters.soma_total_min = Math.max(120, baseMin + 10);
                this.dynamicFilters.soma_total_max = Math.min(300, baseMax - 10);
                break;
                
            case 'conservador':
                // Faixa muito ampla: -30 do min, +30 do max (máxima flexibilidade)
                this.dynamicFilters.soma_total_min = Math.max(150, baseMin - 30);
                this.dynamicFilters.soma_total_max = Math.min(275, baseMax + 30);
                break;
                
            default: // moderado
                // Manter faixa da análise
                this.dynamicFilters.soma_total_min = Math.max(120, baseMin);
                this.dynamicFilters.soma_total_max = Math.min(300, baseMax);
                break;
        }
        
        console.log(`💰 SomaTotal aplicada - Perfil: ${profile}, Base: ${somaAtual}, Faixa: ${this.dynamicFilters.soma_total_min}-${this.dynamicFilters.soma_total_max}`);
    }

    updateFilterValue(filterId, min, max) {
        console.log(`📝 Atualizando ${filterId}: ${min} - ${max}`);
        
        // Mapear IDs para propriedades dos filtros
        const filterMap = {
            'menorQueUltimo': 'menor_que_ultimo',
            'maiorQueUltimo': 'maior_que_ultimo', 
            'igualAoUltimo': 'igual_ao_ultimo'
        };
        
        const filterKey = filterMap[filterId];
        if (filterKey) {
            // Criar array de valores na faixa especificada
            const values = [];
            for (let i = min; i <= max; i++) {
                values.push(i);
            }
            this.dynamicFilters[filterKey] = values;
            console.log(`✅ Filtro ${filterKey} atualizado: [${values.join(', ')}]`);
        }
        
        // Calcular soma total baseada nos filtros (estimativa)
        if (min !== undefined && max !== undefined) {
            // Estimar faixa de soma baseada nos filtros aplicados
            this.updateSomaFilter();
        }
    }

    updateSomaFilter() {
        // Estimar faixa de soma total baseada nos outros filtros
        // Esta is uma estimativa simples - pode ser refinada
        const menorQue = this.dynamicFilters.menor_que_ultimo;
        const maiorQue = this.dynamicFilters.maior_que_ultimo;
        const igualAo = this.dynamicFilters.igual_ao_ultimo;
        
        if (menorQue || maiorQue || igualAo) {
            // Faixa conservadora baseada no perfil de risco
            let baseMin = 168, baseMax = 202; // Faixa padrão para Lotofácil
            
            // Ajustar baseado no perfil
            switch(this.riskProfile) {
                case 'conservador':
                    this.dynamicFilters.soma_total_min = baseMin - 15;
                    this.dynamicFilters.soma_total_max = baseMax + 15;
                    break;
                case 'agressivo':
                    const centro = (baseMin + baseMax) / 2;
                    this.dynamicFilters.soma_total_min = Math.round(centro - 10);
                    this.dynamicFilters.soma_total_max = Math.round(centro + 10);
                    break;
                default: // moderado
                    this.dynamicFilters.soma_total_min = baseMin;
                    this.dynamicFilters.soma_total_max = baseMax;
            }
            
            console.log(`🧮 Soma total estimada: ${this.dynamicFilters.soma_total_min} - ${this.dynamicFilters.soma_total_max}`);
        }
    }
}

// Inicializar quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM carregado, criando LotoScopeWeb...');
    try {
        window.lotoScope = new LotoScopeWeb();
        console.log('✅ LotoScopeWeb criado com sucesso!');
    } catch (error) {
        console.error('❌ Erro ao criar LotoScopeWeb:', error);
    }
});

console.log('📦 LotoScopeWeb carregado!');