import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.services.workflow_executor import WorkflowExecutor


class WorkflowGraphTests(unittest.TestCase):
    def setUp(self):
        self.executor = WorkflowExecutor(db_session=MagicMock())

    def test_topological_sort_orders_dependencies_and_rejects_cycles(self):
        nodes = [
            {"id": "input", "type": "prompt_input"},
            {"id": "first", "type": "api_call"},
            {"id": "second", "type": "api_call"},
        ]
        edges = [
            {"source": "input", "target": "first"},
            {"source": "first", "target": "second"},
        ]

        order = self.executor._topological_sort(nodes, edges)

        self.assertLess(order.index("input"), order.index("first"))
        self.assertLess(order.index("first"), order.index("second"))
        self.assertEqual(
            self.executor._topological_sort(
                nodes,
                edges + [{"source": "second", "target": "first"}],
            ),
            [],
        )

    def test_dependency_readiness_ignores_input_nodes(self):
        nodes = [
            {"id": "input", "type": "prompt_input"},
            {"id": "first", "type": "api_call"},
            {"id": "second", "type": "api_call"},
        ]
        edges = [
            {"source": "input", "target": "second"},
            {"source": "first", "target": "second"},
        ]

        self.assertFalse(
            self.executor._are_dependencies_ready("second", edges, set(), nodes)
        )
        self.assertTrue(
            self.executor._are_dependencies_ready("second", edges, {"first"}, nodes)
        )


class WorkflowExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_multi_node_execution_starts_only_entry_api_nodes(self):
        executor = WorkflowExecutor(db_session=MagicMock())
        executor._execute_node = AsyncMock(
            return_value={"status": "started", "node_id": "first"}
        )
        workflow = SimpleNamespace(
            nodes=[
                {"id": "input", "type": "prompt_input"},
                {"id": "first", "type": "api_call", "api_id": 10},
                {"id": "second", "type": "api_call", "api_id": 20},
            ],
            edges=[
                {"source": "input", "target": "first"},
                {"source": "first", "target": "second"},
            ],
        )

        result = await executor._execute_multi_node(
            workflow, work_id=42, webhook_url="https://example.test/webhook"
        )

        self.assertEqual(result, {"status": "started", "node_id": "first"})
        executor._execute_node.assert_awaited_once_with(
            workflow.nodes[1],
            42,
            "https://example.test/webhook",
            is_final=False,
        )


if __name__ == "__main__":
    unittest.main()
