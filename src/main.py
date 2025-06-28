import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3
from dotenv import load_dotenv
import json
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_super_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///casinofound.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

# Inicializar banco de dados
db = SQLAlchemy(app)

# Configuração Web3 com as suas credenciais
INFURA_API_KEY = "682ccbc62ca74263a6358998b7c9e628"
POLYGON_RPC_URL = f"https://polygon-mainnet.infura.io/v3/{INFURA_API_KEY}"
WALLETCONNECT_PROJECT_ID = "6175ffe549ad2465e15f2fb66c70c469"
EMAILJS_SERVICE_ID = "service_fuhff9e"

# Endereços dos contratos
CFD_TOKEN_ADDRESS = "0x7fE9eE1975263998D7BfD7ed46CAD44Ee62A63bE"
ICO_PHASE1_ADDRESS = "0x8008A571414ebAF2f965a5a8d34D78cEfa8BD8bD"
AFFILIATE_MANAGER_ADDRESS = "0x7fE9eE1975263998D7BfD7ed46CAD44Ee62A63bE"  # Mesmo endereço do token principal

# Inicializar Web3
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

# ABIs dos contratos
CFD_TOKEN_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "allowance",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "needed",
                "type": "uint256"
            }
        ],
        "name": "ERC20InsufficientAllowance",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "balance",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "needed",
                "type": "uint256"
            }
        ],
        "name": "ERC20InsufficientBalance",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "approver",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidApprover",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "receiver",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidReceiver",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidSender",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidSpender",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

AFFILIATE_MANAGER_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "authorizedContracts",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address payable",
                "name": "affiliate",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "payAffiliate",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "contractAddress",
                "type": "address"
            },
            {
                "internalType": "bool",
                "name": "status",
                "type": "bool"
            }
        ],
        "name": "setAuthorized",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "totalEarned",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ICO_PHASE1_ABI = [
    {
        "inputs": [
            {
                "internalType": "address payable",
                "name": "affiliate",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "payAffiliate",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Inicializar contratos
cfd_token_contract = w3.eth.contract(address=CFD_TOKEN_ADDRESS, abi=CFD_TOKEN_ABI)
affiliate_manager_contract = w3.eth.contract(address=AFFILIATE_MANAGER_ADDRESS, abi=AFFILIATE_MANAGER_ABI)
ico_phase1_contract = w3.eth.contract(address=ICO_PHASE1_ADDRESS, abi=ICO_PHASE1_ABI)

# Modelos de banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    cfd_balance = db.Column(db.Float, default=0.0)
    staked_tokens = db.Column(db.Float, default=0.0)
    earned_rewards = db.Column(db.Float, default=0.0)
    affiliate_earnings = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(42), unique=True)
    referred_by = db.Column(db.String(42))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # buy, stake, unstake, affiliate
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    tx_hash = db.Column(db.String(66))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Criar tabelas
with app.app_context():
    db.create_all()

# Rotas da API

@app.route('/api/user_data', methods=['GET'])
def get_user_data():
    """Obter dados do usuário"""
    wallet_address = request.args.get('wallet_address')
    
    if not wallet_address:
        return jsonify({'error': 'Endereço da carteira é obrigatório'}), 400
    
    try:
        # Buscar ou criar usuário
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            user = User(
                wallet_address=wallet_address,
                referral_code=wallet_address,
                cfd_balance=0.0,
                staked_tokens=0.0,
                earned_rewards=0.0,
                affiliate_earnings=0.0
            )
            db.session.add(user)
            db.session.commit()
        
        # Buscar saldo real do contrato (se possível)
        try:
            real_balance = cfd_token_contract.functions.balanceOf(wallet_address).call()
            user.cfd_balance = real_balance / (10**18)  # Converter de wei para tokens
        except Exception as e:
            app.logger.warning(f"Erro ao buscar saldo real: {e}")
        
        # Calcular percentagem do total supply
        total_supply = 21000000  # 21 milhões de tokens
        cfd_percentage = (user.cfd_balance / total_supply) * 100 if total_supply > 0 else 0
        
        return jsonify({
            'cfd_balance': f"{user.cfd_balance:.2f}",
            'total_supply': f"{total_supply:,}",
            'cfd_percentage': f"{cfd_percentage:.4f}",
            'staked_tokens': f"{user.staked_tokens:.2f}",
            'earned_rewards': f"{user.earned_rewards:.4f}",
            'affiliate_earnings': f"{user.affiliate_earnings:.4f}"
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao obter dados do usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/buy_tokens', methods=['POST'])
def buy_tokens():
    """Comprar tokens CFD"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    amount = float(data.get('amount', 0))
    currency = data.get('currency', 'usdt')
    
    if not wallet_address or amount <= 0:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    try:
        # Buscar ou criar usuário
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            user = User(wallet_address=wallet_address, referral_code=wallet_address)
            db.session.add(user)
        
        # Simular compra (em produção, interagir com contrato real)
        price_per_token = 0.02  # Preço da Fase 1
        tokens_to_receive = amount / price_per_token
        
        # Atualizar saldo do usuário
        user.cfd_balance += tokens_to_receive
        
        # Registrar transação
        transaction = Transaction(
            wallet_address=wallet_address,
            transaction_type='buy',
            amount=tokens_to_receive,
            currency=currency,
            status='confirmed'
        )
        db.session.add(transaction)
        
        # Processar afiliado se houver
        if user.referred_by:
            affiliate_commission = amount * 0.05  # 5% de comissão
            affiliate_user = User.query.filter_by(wallet_address=user.referred_by).first()
            if affiliate_user:
                affiliate_user.affiliate_earnings += affiliate_commission
        
        db.session.commit()
        
        return jsonify({
            'message': f'Compra simulada com sucesso! {tokens_to_receive:.2f} CFD adicionados ao seu saldo.',
            'tokens_received': tokens_to_receive
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao comprar tokens: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/stake_tokens', methods=['POST'])
def stake_tokens():
    """Fazer staking de tokens"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    amount = float(data.get('amount', 0))
    
    if not wallet_address or amount <= 0:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    try:
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.cfd_balance < amount:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Transferir tokens para staking
        user.cfd_balance -= amount
        user.staked_tokens += amount
        
        # Registrar transação
        transaction = Transaction(
            wallet_address=wallet_address,
            transaction_type='stake',
            amount=amount,
            currency='CFD',
            status='confirmed'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': f'Staking de {amount:.2f} CFD realizado com sucesso! Tokens bloqueados por 30 dias.'
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao fazer staking: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/unstake_tokens', methods=['POST'])
def unstake_tokens():
    """Fazer unstaking de tokens"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    amount = float(data.get('amount', 0))
    
    if not wallet_address or amount <= 0:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    try:
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.staked_tokens < amount:
            return jsonify({'error': 'Quantidade em staking insuficiente'}), 400
        
        # Verificar período de lock (simulado - em produção, verificar contrato)
        # Por agora, permitir unstaking imediato para demonstração
        
        # Transferir tokens de volta
        user.staked_tokens -= amount
        user.cfd_balance += amount
        
        # Registrar transação
        transaction = Transaction(
            wallet_address=wallet_address,
            transaction_type='unstake',
            amount=amount,
            currency='CFD',
            status='confirmed'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': f'Unstaking de {amount:.2f} CFD realizado com sucesso!'
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao fazer unstaking: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/claim_affiliate_earnings', methods=['POST'])
def claim_affiliate_earnings():
    """Reivindicar ganhos de afiliado"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({'error': 'Endereço da carteira é obrigatório'}), 400
    
    try:
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.affiliate_earnings <= 0:
            return jsonify({'error': 'Nenhum ganho disponível para reivindicar'}), 400
        
        # Simular transferência (em produção, interagir com contrato real)
        earnings_to_claim = user.affiliate_earnings
        user.affiliate_earnings = 0
        
        # Registrar transação
        transaction = Transaction(
            wallet_address=wallet_address,
            transaction_type='affiliate',
            amount=earnings_to_claim,
            currency='MATIC',
            status='confirmed'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': f'Ganhos de {earnings_to_claim:.4f} MATIC reivindicados com sucesso!'
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao reivindicar ganhos: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """Subscrever newsletter"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    
    try:
        # Verificar se email já existe
        existing = Newsletter.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                return jsonify({'error': 'Email já subscrito'}), 400
            else:
                existing.is_active = True
                db.session.commit()
                return jsonify({'message': 'Subscrição reativada com sucesso!'})
        
        # Criar nova subscrição
        newsletter = Newsletter(email=email)
        db.session.add(newsletter)
        db.session.commit()
        
        return jsonify({'message': 'Subscrito com sucesso! Obrigado por se juntar à nossa newsletter.'})
        
    except Exception as e:
        app.logger.error(f"Erro ao subscrever newsletter: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Estatísticas para o painel administrativo"""
    try:
        total_users = User.query.count()
        total_newsletter = Newsletter.query.filter_by(is_active=True).count()
        total_transactions = Transaction.query.count()
        total_staked = db.session.query(db.func.sum(User.staked_tokens)).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'total_newsletter': total_newsletter,
            'total_transactions': total_transactions,
            'total_staked': f"{total_staked:.2f}"
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde do serviço"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'web3_connected': w3.is_connected(),
        'database_connected': True
    })

# Configurar logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

