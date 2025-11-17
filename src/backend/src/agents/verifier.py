"""Agente Verificador - Valida qualidade e compliance."""
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from src.workflows.schema import VerifiedResponse, GeneratedResponse
from src.utils.metrics import (
    verifier_validations_total,
    verifier_detections_total,
    verifier_confidence_scores
)
from src.utils.langfuse_wrapper import observe
import logging
import re
import json

logger = logging.getLogger(__name__)


class VerifierAgent:
    """Agente Verificador para validação de respostas."""
    
    def __init__(self, llm: BaseChatModel):
        """Inicializar Agente Verificador."""
        self.llm = llm
        self.prohibited_terms = self._load_prohibited_terms()
        self._setup_system_prompt()
        logger.info("VerifierAgent inicializado")
    
    def _load_prohibited_terms(self) -> List[str]:
        """Carregar lista de termos proibidos."""
        # TODO: Carregar de arquivo de configuração
        return [
            "garantimos 100%",
            "sem exceções",
            "sempre",
            "nunca falha",
            "garantia absoluta",
            "100% garantido",
            "zero falhas",
            "perfeito",
            "infalível"
        ]
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Verificador especializado em validar qualidade e compliance de respostas.
Sua função é:
1. Verificar consistência entre respostas
2. Detectar termos proibidos
3. Identificar lacunas
4. Validar limites contratuais
5. Calcular score de confiança

Sempre responda de forma objetiva e precisa."""
    
    def check_consistency(
        self,
        responses: List[GeneratedResponse]
    ) -> Dict[str, Any]:
        """Verificar consistência entre respostas relacionadas."""
        logger.info(f"Verificando consistência de {len(responses)} respostas")
        inconsistencies = []
        
        # Agrupar por categoria (assumindo que qid pode ter formato Q001, Q002, etc.)
        by_category = {}
        for resp in responses:
            # Tentar extrair categoria do qid ou usar 'general'
            category = 'general'
            if '_' in resp.qid:
                category = resp.qid.split('_')[0]
            elif resp.qid.startswith('Q'):
                # Assumir que todas as perguntas numéricas são da mesma categoria
                category = 'questionnaire'
            
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(resp)
        
        # Verificar contradições
        for category, category_responses in by_category.items():
            if len(category_responses) > 1:
                # Comparar respostas da mesma categoria
                for i, resp1 in enumerate(category_responses):
                    for resp2 in category_responses[i+1:]:
                        if self._are_contradictory(resp1, resp2):
                            inconsistencies.append({
                                "qid1": resp1.qid,
                                "qid2": resp2.qid,
                                "issue": "Contradição detectada entre respostas",
                                "response1": resp1.response_text[:100],
                                "response2": resp2.response_text[:100]
                            })
        
        result = {
            "is_consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies
        }
        
        if inconsistencies:
            logger.warning(f"Encontradas {len(inconsistencies)} inconsistências")
            for inc in inconsistencies:
                verifier_detections_total.labels(type="inconsistencies").inc()
        
        return result
    
    def _are_contradictory(
        self,
        resp1: GeneratedResponse,
        resp2: GeneratedResponse
    ) -> bool:
        """Verificar se duas respostas são contraditórias usando LLM."""
        try:
            prompt = f"""Analise as seguintes respostas e determine se elas são contraditórias.

Resposta 1: {resp1.response_text[:500]}
Resposta 2: {resp2.response_text[:500]}

As respostas se contradizem? Responda APENAS com "SIM" ou "NÃO"."""
            
            messages = [
                SystemMessage(content="Você é um verificador de consistência. Responda apenas SIM ou NÃO."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            content_upper = content.strip().upper()
            
            # Verificar se resposta contém "SIM"
            is_contradictory = "SIM" in content_upper or "YES" in content_upper
            
            if is_contradictory:
                logger.debug(f"Contradição detectada entre {resp1.qid} e {resp2.qid}")
            
            return is_contradictory
            
        except Exception as e:
            logger.error(f"Erro ao verificar contradição: {e}")
            # Em caso de erro, assumir que não são contraditórias
            return False
    
    def detect_prohibited_terms(self, response_text: str) -> List[str]:
        """Detectar termos proibidos na resposta."""
        detected = []
        text_lower = response_text.lower()
        
        for term in self.prohibited_terms:
            if term.lower() in text_lower:
                detected.append(term)
                logger.warning(f"Termo proibido detectado: {term}")
                verifier_detections_total.labels(type="prohibited_terms").inc()
        
        return detected
    
    def detect_gaps(
        self,
        question: str,
        response: GeneratedResponse
    ) -> List[str]:
        """Detectar lacunas na resposta."""
        gaps = []
        
        # Verificar se resposta está vazia ou muito curta
        if not response.response_text or len(response.response_text.strip()) < 10:
            gaps.append("Resposta muito curta ou vazia")
            logger.warning(f"Resposta muito curta para {response.qid}")
        
        # Verificar campos obrigatórios mencionados na pergunta
        required_keywords = {
            "sla": ["sla", "disponibilidade", "uptime", "tempo de atividade"],
            "garantia": ["garantia", "warranty", "cobertura"],
            "suporte": ["suporte", "support", "atendimento", "assistência"],
            "preço": ["preço", "price", "custo", "valor", "tarifa"],
            "prazo": ["prazo", "deadline", "entrega", "tempo"],
            "segurança": ["segurança", "security", "proteção", "privacidade"]
        }
        
        question_lower = question.lower()
        response_lower = response.response_text.lower()
        
        for keyword, synonyms in required_keywords.items():
            # Verificar se pergunta menciona o tópico
            question_mentions = any(syn in question_lower for syn in synonyms)
            
            if question_mentions:
                # Verificar se resposta menciona o tópico
                response_mentions = any(syn in response_lower for syn in synonyms)
                
                if not response_mentions:
                    gaps.append(f"Falta mencionar: {keyword}")
                    logger.warning(f"Lacuna detectada: falta mencionar {keyword} em {response.qid}")
        
        if gaps:
            for gap in gaps:
                verifier_detections_total.labels(type="gaps").inc()
        
        return gaps
    
    def validate_contractual_limits(
        self,
        response_text: str
    ) -> Dict[str, Any]:
        """Validar aderência a limites contratuais."""
        violations = []
        
        # Verificar promessas excessivas (ex: 100% de disponibilidade)
        if re.search(r'100\s*%', response_text, re.IGNORECASE):
            violations.append("Promessa de 100% pode ser problemática contratualmente")
        
        # Verificar termos absolutos
        absolute_terms = ["sempre", "nunca", "todos", "nenhum"]
        for term in absolute_terms:
            if re.search(rf'\b{term}\b', response_text, re.IGNORECASE):
                violations.append(f"Uso de termo absoluto: {term}")
        
        # TODO: Implementar validação baseada em regras configuráveis
        # Por enquanto, apenas verificar padrões básicos
        
        result = {
            "is_valid": len(violations) == 0,
            "violations": violations
        }
        
        if violations:
            logger.warning(f"Violações contratuais detectadas: {violations}")
            for violation in violations:
                verifier_detections_total.labels(type="contractual_violations").inc()
        
        return result
    
    def verify_formatting(
        self,
        response_text: str,
        expected_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verificar se resposta está no formato esperado."""
        if not expected_format:
            return {"is_valid": True, "errors": []}
        
        errors = []
        
        if expected_format == "sim/não" or expected_format == "yes/no":
            response_clean = response_text.lower().strip()
            valid_responses = ["sim", "não", "yes", "no", "s", "n"]
            if response_clean not in valid_responses:
                errors.append(f"Formato esperado: sim/não. Recebido: {response_text[:50]}")
        
        elif expected_format == "número" or expected_format == "number":
            if not re.search(r'\d+', response_text):
                errors.append("Formato esperado: número. Nenhum número encontrado na resposta")
        
        elif expected_format == "lista" or expected_format == "list":
            has_list_indicators = (
                "\n" in response_text or
                "-" in response_text or
                "," in response_text or
                ";" in response_text
            )
            if not has_list_indicators:
                errors.append("Formato esperado: lista. Estrutura de lista não encontrada")
        
        elif expected_format == "data" or expected_format == "date":
            # Verificar formatos de data comuns
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}-\d{1,2}-\d{4}'
            ]
            has_date = any(re.search(pattern, response_text) for pattern in date_patterns)
            if not has_date:
                errors.append("Formato esperado: data. Nenhuma data encontrada na resposta")
        
        # Formato texto aceita qualquer coisa
        result = {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
        
        if errors:
            logger.warning(f"Erros de formatação: {errors}")
            for error in errors:
                verifier_detections_total.labels(type="formatting_errors").inc()
        
        return result
    
    def calculate_confidence_score(
        self,
        response: GeneratedResponse,
        verification_results: Dict[str, Any]
    ) -> float:
        """Calcular score de confiança (0-100%)."""
        score = response.confidence_score * 100
        
        # Reduzir score baseado em problemas encontrados
        if verification_results.get("has_prohibited_terms"):
            score -= 20
            logger.debug("Score reduzido por termos proibidos: -20")
        
        if verification_results.get("has_gaps"):
            gap_penalty = min(15 * len(verification_results.get("gaps", [])), 30)
            score -= gap_penalty
            logger.debug(f"Score reduzido por lacunas: -{gap_penalty}")
        
        if not verification_results.get("is_consistent"):
            score -= 10
            logger.debug("Score reduzido por inconsistência: -10")
        
        if verification_results.get("formatting_errors"):
            formatting_errors = verification_results.get("formatting_errors", [])
            score -= 5 * len(formatting_errors)
            logger.debug(f"Score reduzido por erros de formatação: -{5 * len(formatting_errors)}")
        
        if not verification_results.get("contractual_valid"):
            score -= 15
            logger.debug("Score reduzido por violações contratuais: -15")
        
        final_score = max(0.0, min(100.0, score))
        logger.debug(f"Score final calculado: {final_score:.2f}%")
        
        # Registrar métrica de confidence score (normalizado para 0-1)
        verifier_confidence_scores.observe(final_score / 100.0)
        
        return final_score
    
    @observe(name="verifier_verify")
    def verify(
        self,
        question: str,
        response: GeneratedResponse,
        all_responses: Optional[List[GeneratedResponse]] = None,
        expected_format: Optional[str] = None
    ) -> VerifiedResponse:
        """Verificar resposta completa."""
        logger.info(f"Verificando resposta {response.qid}")
        
        all_responses = all_responses or [response]
        
        # Verificar consistência
        consistency = self.check_consistency(all_responses)
        
        # Detectar termos proibidos
        prohibited = self.detect_prohibited_terms(response.response_text)
        
        # Detectar lacunas
        gaps = self.detect_gaps(question, response)
        
        # Validar limites contratuais
        contractual = self.validate_contractual_limits(response.response_text)
        
        # Verificar formatação
        formatting_result = self.verify_formatting(response.response_text, expected_format)
        
        # Calcular score
        verification_results = {
            "is_consistent": consistency["is_consistent"],
            "has_prohibited_terms": len(prohibited) > 0,
            "prohibited_terms": prohibited,
            "has_gaps": len(gaps) > 0,
            "gaps": gaps,
            "contractual_valid": contractual["is_valid"],
            "contractual_violations": contractual["violations"],
            "formatting_ok": formatting_result["is_valid"],
            "formatting_errors": formatting_result["errors"]
        }
        
        confidence_score = self.calculate_confidence_score(response, verification_results)
        
        # Determinar se precisa revisão
        needs_review = (
            not consistency["is_consistent"] or
            len(prohibited) > 0 or
            len(gaps) > 0 or
            not contractual["is_valid"] or
            not formatting_result["is_valid"] or
            confidence_score < 70.0
        )
        
        # Coletar todos os erros de validação
        validation_errors = []
        validation_errors.extend([inc.get("issue", "Inconsistência") for inc in consistency["inconsistencies"]])
        validation_errors.extend(gaps)
        validation_errors.extend(contractual["violations"])
        validation_errors.extend(formatting_result["errors"])
        
        # Métricas
        status = "needs_review" if needs_review else "approved"
        verifier_validations_total.labels(status=status).inc()
        
        verified_response = VerifiedResponse(
            qid=response.qid,
            response_text=response.response_text,
            confidence_score=confidence_score / 100.0,
            is_consistent=consistency["is_consistent"],
            has_prohibited_terms=len(prohibited) > 0,
            has_gaps=len(gaps) > 0,
            validation_errors=validation_errors,
            needs_review=needs_review
        )
        
        logger.info(
            f"Verificação completa para {response.qid}: "
            f"confiança={confidence_score:.1f}%, "
            f"revisão={'sim' if needs_review else 'não'}"
        )
        
        return verified_response
    
    def verify_batch(
        self,
        questions_and_responses: List[Dict[str, Any]],
        expected_formats: Optional[Dict[str, str]] = None
    ) -> List[VerifiedResponse]:
        """Verificar múltiplas respostas em lote."""
        logger.info(f"Verificando lote de {len(questions_and_responses)} respostas")
        
        all_responses = [item["response"] for item in questions_and_responses]
        verified_responses = []
        
        for item in questions_and_responses:
            question = item["question"]
            response = item["response"]
            qid = response.qid
            
            expected_format = None
            if expected_formats and qid in expected_formats:
                expected_format = expected_formats[qid]
            
            verified = self.verify(
                question=question,
                response=response,
                all_responses=all_responses,
                expected_format=expected_format
            )
            verified_responses.append(verified)
        
        logger.info(f"Verificação de lote concluída: {len(verified_responses)} respostas verificadas")
        return verified_responses
