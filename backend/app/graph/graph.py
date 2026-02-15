"""
LangGraph workflow definition for the support agent.
Defines nodes, edges, and state transitions.
"""
from langgraph.graph import StateGraph, END

from app.graph.state import SupportState
from app.graph.nodes.intent import detect_intent
from app.graph.nodes.solution import generate_solution
from app.graph.edges import route_after_solution, route_after_intent
from app.services.escalation import build_escalation_payload


def escalate_node(state: dict) -> dict:
    """
    Prepare escalation payload for human review.
    """
    return {
        "status": "waiting_human",
        "needs_human": True,
        "final_response": build_escalation_payload(state)
    }


def explicit_escalate_node(state: dict) -> dict:
    """
    Handle explicit escalation request from user.
    Provides a clear message that human support is being connected.
    """
    return {
        "status": "waiting_human",
        "needs_human": True,
        "proposed_solution": "I understand you'd like to speak with a human agent. I'm escalating your ticket now. A support representative will review your case and get back to you shortly.",
        "final_response": {
            "message": "Ticket escalated to human support",
            "reason": "User explicitly requested human assistance",
            "ticket_id": state["ticket_id"]
        }
    }


def finalize_resolved(state: dict) -> dict:
    """
    Finalize a successfully resolved ticket.
    """
    return {
        "status": "resolved",
        "final_response": {
            "message": "Your issue has been resolved",
            "solution": state.get("proposed_solution"),
            "ticket_id": state["ticket_id"]
        }
    }


def off_topic_node(state: dict) -> dict:
    """
    Handle off-topic messages that aren't support requests.
    Returns a polite response without creating a real ticket.
    """
    return {
        "status": "dismissed",
        "needs_human": False,
        "proposed_solution": "I'm a customer support assistant. I can help you with billing questions, technical issues, account problems, refunds, and other support requests. Please describe the issue you're facing, and I'll create a support ticket for you.",
        "final_response": {
            "message": "Off-topic message handled",
            "ticket_id": state["ticket_id"]
        }
    }


def build_graph() -> StateGraph:
    """
    Build and compile the support agent workflow graph.
    
    Flow:
    1. intent -> Classify ticket intent (check for explicit escalation)
    2. If explicit escalation -> immediate_escalate
       Else -> solution -> Conditional: escalate or finalize
    """
    graph = StateGraph(SupportState)

    # Add nodes
    graph.add_node("intent", detect_intent)
    graph.add_node("solution", generate_solution)
    graph.add_node("escalate", escalate_node)
    graph.add_node("immediate_escalate", explicit_escalate_node)
    graph.add_node("off_topic", off_topic_node)
    graph.add_node("finalize", finalize_resolved)

    # Set entry point
    graph.set_entry_point("intent")

    # Conditional routing after intent - check for explicit escalation or off-topic
    graph.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "escalate": "immediate_escalate",
            "off_topic": "off_topic",
            "continue": "solution"
        }
    )

    # Conditional routing after solution
    graph.add_conditional_edges(
        "solution",
        route_after_solution,
        {
            "escalate": "escalate",
            "finish": "finalize"
        }
    )

    # Terminal edges
    graph.add_edge("escalate", END)
    graph.add_edge("immediate_escalate", END)
    graph.add_edge("off_topic", END)
    graph.add_edge("finalize", END)

    return graph.compile()

