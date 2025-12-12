from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
import uuid
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_db
from backend.shared.models import ChatRequest, ChatResponse, ResponseModel, MessageRole
from backend.database.models import Conversation, Message, User
from agent import TravelAgent

router = APIRouter()

# Initialize the travel agent
travel_agent = TravelAgent()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to the AI travel agent

    The agent will:
    - Understand user intent
    - Ask clarifying questions
    - Search for flights, hotels, weather using appropriate tools
    - Provide personalized recommendations
    """

    # Get or create conversation
    conversation_id = request.conversation_id or str(uuid.uuid4())

    conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )

    if not conversation:
        # Create new conversation
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=request.user_id,
            context=request.context.model_dump() if request.context else {},
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message to database
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content=request.message,
    )
    db.add(user_message)
    db.commit()

    # Get user context for personalization
    user = db.query(User).filter(User.id == request.user_id).first()
    user_context = {}
    if user and user.preferences:
        user_context["preferences"] = user.preferences

    if request.context:
        user_context.update(request.context.model_dump())

    # Get response from agent
    response = await travel_agent.chat(
        message=request.message,
        conversation_id=conversation_id,
        user_context=user_context,
    )

    # Save assistant message to database
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT.value,
        content=response["message"],
        metadata={"suggestions": response.get("suggestions", [])},
    )
    db.add(assistant_message)

    # Update conversation
    conversation.updated_at = datetime.now()
    db.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        message=response["message"],
        suggestions=response.get("suggestions"),
    )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation history"""

    conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .all()
    )

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at,
                "metadata": msg.metadata,
            }
            for msg in messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation and its history"""

    conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Clear from agent memory
    travel_agent.clear_conversation(conversation_id)

    # Delete from database
    db.delete(conversation)
    db.commit()

    return ResponseModel(
        success=True,
        message="Conversation deleted successfully",
    )


@router.get("/conversations/user/{user_id}")
async def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a user"""

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return {
        "conversations": [
            {
                "conversation_id": conv.conversation_id,
                "title": conv.title or "New Conversation",
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages),
            }
            for conv in conversations
        ]
    }
