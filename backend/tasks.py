import psutil
from datetime import datetime
import asyncio
from typing import TYPE_CHECKING
from nexon.data.models import MetricsCollector, BotUser

if TYPE_CHECKING:
    from .apiManager import APIServer

async def collect_metrics(backend: 'APIServer'):
    """Collect and store system and bot metrics every minute"""
    while True:
        try:
            process = psutil.Process()
            bot, _ = await BotUser.get_or_create_bot()
            
            # Collect system stats
            system_stats = {
                'cpu_usage': round(psutil.cpu_percent(), 2),
                'memory_usage': round(process.memory_percent(), 2),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': round(psutil.disk_usage('/').percent, 2),
                'thread_count': process.num_threads()
            }
            
            # Collect bot stats
            bot_stats = {
                'latency': round(backend.client.latency * 1000),
                'guild_count': len(backend.client.guilds),
                'user_count': sum(g.member_count or 0 for g in backend.client.guilds),
                'channel_count': sum(len(g.channels) for g in backend.client.guilds),
                'voice_connections': len(backend.client.voice_clients),
                'commands_processed': bot.commands_processed,
                'messages_sent': bot.total_messages,
                'errors_encountered': bot.errors_encountered
            }
            
            # Store metrics
            
            await MetricsCollector.add_metrics(system_stats, bot_stats)
            
        except Exception as e:
            backend.logger.error(f"Error collecting metrics: {e}")
        
        await asyncio.sleep(60)

async def start_tasks(backend: 'APIServer'):
    """Start all background tasks"""
    backend.logger.info("Starting background tasks...")
    asyncio.create_task(collect_metrics(backend))