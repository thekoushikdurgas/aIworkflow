"""
Workflows manager: build and run chained tool workflows.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger
from utils.storage import StoragePaths, read_json, write_json
import streamlit as st

from config.settings import AppSettings
from .tool_workshop import ToolWorkshopInterface


logger = get_logger(__name__)

class WorkflowsInterface:
    """Workflow builder and executor UI."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.workflows_dir = StoragePaths.ROOT_MAP["@workflows"]
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        # Reuse tool loading/execution from ToolWorkshopInterface
        self.tools = ToolWorkshopInterface(settings)

    # ---------- Persistence ----------
    def _list_workflows(self) -> List[str]:
        return [p.stem for p in self.workflows_dir.glob("*.json")]

    def _load_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            return read_json("@workflows", f"{name}.json")
        except Exception as e:
            st.error(f"Error loading workflow {name}: {e}")
            logger.error(f"Error loading workflow {name}: {e}")
            return None

    def _save_workflow(self, data: Dict[str, Any]) -> bool:
        try:
            name = data.get("name")
            if not name:
                st.error("Workflow must have a name")
                return False
            ok = write_json("@workflows", f"{name}.json", data)
            if ok:
                logger.info(f"Saved workflow {name}")
            return ok
        except Exception as e:
            st.error(f"Error saving workflow: {e}")
            logger.error(f"Error saving workflow: {e}")
            return False

    # ---------- Execution ----------
    def _execute_workflow(self, workflow: Dict[str, Any], top_params: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Dict[str, Any]], Optional[str]]:
        """Run steps sequentially; each step can take inputs from previous outputs or constants.

        Returns (ok, step_results, final_output_json_str)
        """
        steps: List[Dict[str, Any]] = workflow.get("steps", [])
        if not steps:
            return False, [], "{}"

        step_outputs: List[Dict[str, Any]] = []
        final_json_str: Optional[str] = None

        for idx, step in enumerate(steps):
            tool_name: str = step.get("tool")
            if not tool_name:
                return False, step_outputs, json.dumps({"error": f"Step {idx+1} missing tool"})

            # Build parameters
            params: Dict[str, Any] = {}
            input_map: Dict[str, Any] = step.get("inputs", {})

            # Retrieve tool config to know required inputs; fallback to provided mapping
            tool_cfg = self.tools.load_tool_config(tool_name) or {}
            tool_inputs = tool_cfg.get("input_parameters", tool_cfg.get("parameters", []))

            # For each declared mapping, resolve source
            for key, mapping in input_map.items():
                # mapping can be {"type":"const","value":...} or {"type":"ref","step":i,"output":"name"}
                try:
                    mtype = mapping.get("type") if isinstance(mapping, dict) else "const"
                    if mtype == "ref":
                        ref_step = int(mapping.get("step", -1))
                        ref_output = mapping.get("output")
                        if ref_step < 0 or ref_step >= len(step_outputs):
                            st.error(f"Invalid reference for input '{key}' at step {idx+1}")
                            return False, step_outputs, json.dumps({"error": f"Invalid ref for '{key}'"})
                        params[key] = step_outputs[ref_step].get(ref_output)
                    elif mtype == "param":
                        # Reference a top-level workflow parameter by name
                        if top_params is None:
                            return False, step_outputs, json.dumps({"error": f"No top-level params provided for '{key}'"})
                        p_name = mapping.get("name")
                        if p_name not in top_params:
                            return False, step_outputs, json.dumps({"error": f"Top-level param '{p_name}' not provided for '{key}'"})
                        params[key] = top_params.get(p_name)
                    else:
                        # Treat everything else as constant
                        params[key] = mapping.get("value") if isinstance(mapping, dict) else mapping
                except Exception as e:
                    return False, step_outputs, json.dumps({"error": f"Input mapping error for '{key}': {e}"})

            # Ensure required inputs exist (best-effort)
            for p in tool_inputs:
                if p.get("required", False):
                    pname = p.get("name")
                    if pname and pname not in params:
                        return False, step_outputs, json.dumps({"error": f"Missing required input '{pname}' for tool '{tool_name}' at step {idx+1}"})

            # Execute tool
            output_str = self.tools.execute_tool(tool_name, params)
            final_json_str = output_str

            # Attempt to parse as JSON; if not JSON, wrap in {"result": str}
            try:
                parsed = json.loads(output_str)
                step_outputs.append(parsed if isinstance(parsed, dict) else {"result": parsed})
            except Exception:
                step_outputs.append({"result": output_str})

        return True, step_outputs, final_json_str

    def _record_workflow_history(self, workflow_name: str, workflow_def: Dict[str, Any], inputs: Dict[str, Any], 
                                 success: bool, final_output: Optional[str], start_time: float,
                                 step_results: List[Dict[str, Any]]) -> None:
        """Append workflow execution history to current session in memory and on disk."""
        try:
            duration = max(0.0, time.time() - start_time)
            entry = {
                "timestamp": time.time(),
                "workflow_name": workflow_name,
                "inputs": inputs or {},
                "step_count": len(workflow_def.get("steps", [])),
                "success": success,
                "execution_time": round(duration, 3),
                "final_output": (final_output[:2000] if isinstance(final_output, str) else str(final_output)) if final_output is not None else None,
                "step_results": step_results
            }

            # In-memory list
            if "workflow_history" not in st.session_state:
                st.session_state.workflow_history = []
            st.session_state.workflow_history.append(entry)
            # if len(st.session_state.workflow_history) > 200:
            #     st.session_state.workflow_history = st.session_state.workflow_history[-200:]

            # Persist on disk alongside current session
            session_id = st.session_state.get("current_session_id")
            if session_id:
                import os
                os.makedirs("output/sessions", exist_ok=True)
                session_path = f"output/sessions/{session_id}.json"
                session_data = {}
                try:
                    if os.path.exists(session_path):
                        with open(session_path, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                except Exception:
                    session_data = {}

                history_list = session_data.get("workflow_history", [])
                history_list.append(entry)
                if len(history_list) > 500:
                    history_list = history_list[-500:]
                session_data["workflow_history"] = history_list

                try:
                    with open(session_path, "w", encoding="utf-8") as f:
                        json.dump(session_data, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- UI helpers ----------
    def _render_step_editor(self, step_idx: int, step: Dict[str, Any], available_tools: Dict[str, Dict[str, Any]], prior_steps: List[Dict[str, Any]]):
        st.markdown(f"**Step {step_idx + 1}**")
        cols = st.columns([2, 1])
        with cols[0]:
            tool_name = st.selectbox(
                "Tool",
                options=[""] + list(available_tools.keys()),
                index=(list(available_tools.keys()).index(step.get("tool")) + 1) if step.get("tool") in available_tools else 0,
                key=f"wf_step_tool_{step_idx}"
            )
            step["tool"] = tool_name

        with cols[1]:
            if st.button("🗑️ Remove Step", key=f"wf_remove_step_{step_idx}"):
                st.session_state.wf_steps.pop(step_idx)
                st.rerun()

        if not tool_name:
            st.info("Select a tool to configure inputs")
            return

        tool_cfg = available_tools.get(tool_name, {})
        input_params = tool_cfg.get("input_parameters", tool_cfg.get("parameters", []))
        output_params = tool_cfg.get("output_parameters", [])

        # Build prior outputs list [(label, (step_idx, output_name))]
        prior_outputs: List[Tuple[str, Tuple[int, str]]] = []
        for i, ps in enumerate(prior_steps):
            for outp in ps.get("output_parameters", []):
                out_name = outp.get("name")
                if out_name:
                    prior_outputs.append((f"Step {i+1}: {ps.get('name', ps.get('tool',''))} → {out_name}", (i, out_name)))

        st.markdown("Inputs")
        if "inputs" not in step:
            step["inputs"] = {}

        for p in input_params:
            pname = p.get("name", "param")
            pdesc = p.get("description", "")
            with st.expander(f"{pname}", expanded=False):
                mode = st.radio(
                    f"Source for '{pname}'",
                    options=["Constant", "From previous step"],
                    horizontal=True,
                    key=f"wf_in_mode_{step_idx}_{pname}"
                )

                if mode == "Constant":
                    default = step["inputs"].get(pname, {}).get("value") if isinstance(step["inputs"].get(pname), dict) else step["inputs"].get(pname)
                    val = st.text_area(
                        "Value (JSON or plain text)",
                        value=json.dumps(default) if isinstance(default, (dict, list)) else (default or ""),
                        key=f"wf_in_const_{step_idx}_{pname}",
                        help=pdesc
                    )
                    # Try to parse JSON, otherwise keep as string
                    try:
                        parsed_val = json.loads(val)
                    except Exception:
                        parsed_val = val
                    step["inputs"][pname] = {"type": "const", "value": parsed_val}
                else:
                    if prior_outputs:
                        labels = [lbl for lbl, _ in prior_outputs]
                        sel = st.selectbox(
                            "Pick previous output",
                            options=[""] + labels,
                            key=f"wf_in_ref_{step_idx}_{pname}"
                        )
                        if sel:
                            idx_label = labels.index(sel)
                            ref_step, ref_out = prior_outputs[idx_label][1]
                            step["inputs"][pname] = {"type": "ref", "step": ref_step, "output": ref_out}
                    else:
                        st.warning("No previous step outputs available")

        if output_params:
            st.caption("This tool exposes outputs: " + ", ".join([p.get("name", "result") for p in output_params]))

    # ---------- Render ----------
    def render(self):
        st.markdown("# 🔗 Workflows")
        st.caption("Chain tools so outputs feed into subsequent inputs. Save and run workflows.")

        all_tools = self.tools.load_all_tools()

        tabs = st.tabs(["▶️ Run", "🛠️ Build / Edit", "📁 Manage"]) 

        # Run tab
        with tabs[0]:
            workflows = self._list_workflows()
            if not workflows:
                st.info("No workflows found. Create one in the Build tab.")
            else:
                # wf_name = st.selectbox("Workflow", options=workflows, key="wf_run_select")
                for wf_name in workflows:
                    with st.expander(f"Workflow: {wf_name}", expanded=False):
                        if wf_name:
                            wf_data = self._load_workflow(wf_name)
                            # Render input parameters if defined
                            top_inputs = wf_data.get("input_parameters", [])
                            user_params: Dict[str, Any] = {}

                            if top_inputs:
                                st.markdown("### 📥 Inputs")
                                with st.form(f"wf_run_params_form_{wf_name}"):
                                    for p in top_inputs:
                                        pname = p.get("name", "param")
                                        ptype = p.get("type", "string")
                                        pdesc = p.get("description", "")
                                        required = p.get("required", False)

                                        label = f"{pname}{' *' if required else ''}"
                                        if ptype in ["string", "str"]:
                                            user_params[pname] = st.text_input(label, placeholder=pdesc, key=f"wf_run_{pname}")
                                        elif ptype in ["number", "float"]:
                                            user_params[pname] = st.number_input(label, key=f"wf_run_{pname}")
                                        elif ptype in ["integer", "int"]:
                                            val = st.number_input(label, step=1, key=f"wf_run_{pname}")
                                            user_params[pname] = int(val)
                                        elif ptype in ["boolean", "bool"]:
                                            user_params[pname] = st.checkbox(label, key=f"wf_run_{pname}")
                                        elif ptype in ["array", "list"]:
                                            raw = st.text_area(label + " (JSON array)", placeholder=pdesc or "[1,2,3] or [\"a\",\"b\"]", key=f"wf_run_{pname}")
                                            try:
                                                user_params[pname] = json.loads(raw) if raw.strip() else []
                                            except Exception:
                                                user_params[pname] = []
                                                st.warning(f"Invalid JSON for {pname}; using empty list")
                                        elif ptype in ["object", "dict"]:
                                            raw = st.text_area(label + " (JSON)", placeholder=pdesc or '{"key":"value"}', key=f"wf_run_{pname}")
                                            try:
                                                user_params[pname] = json.loads(raw) if raw.strip() else {}
                                            except Exception:
                                                user_params[pname] = {}
                                                st.warning(f"Invalid JSON for {pname}; using empty object")
                                        elif ptype == "file":
                                            up = st.file_uploader(label, key=f"wf_run_{pname}")
                                            if up is not None:
                                                content = up.read()
                                                user_params[pname] = {
                                                    "name": up.name,
                                                    "content": content,
                                                    "type": up.type,
                                                    "size": len(content)
                                                }
                                            else:
                                                user_params[pname] = None
                                        else:
                                            user_params[pname] = st.text_input(label, placeholder=pdesc, key=f"wf_run_{pname}")

                                    exec_clicked = st.form_submit_button("▶️ Execute", type="primary")
                            else:
                                exec_clicked = st.button("▶️ Execute", type="primary")

                            if exec_clicked:
                                with st.spinner(f"Executing workflow '{wf_name}'..."):
                                    _start = time.time()
                                    ok, step_results, final_str = self._execute_workflow(wf_data, user_params if top_inputs else None)
                                    if ok:
                                        st.success("Workflow executed")
                                        with st.expander("Step Results", expanded=False):
                                            for i, res in enumerate(step_results, 1):
                                                st.markdown(f"### Step {i}")
                                                st.json(res)
                                        st.markdown("### 🧩 Final Output")
                                        # Try to align with output_parameters
                                        outs = wf_data.get("output_parameters", [])
                                        if outs:
                                            try:
                                                parsed_final = json.loads(final_str or "{}")
                                            except Exception:
                                                parsed_final = {"result": final_str}
                                            for p in outs:
                                                oname = p.get("name")
                                                if oname:
                                                    st.markdown(f"**{oname}**")
                                                    st.code(json.dumps(parsed_final.get(oname), indent=2) if isinstance(parsed_final.get(oname), (dict, list)) else str(parsed_final.get(oname)), language="json")
                                        # if type(final_str) == str:
                                        # logger.info(f"Final str: {final_str} {type(final_str)}")
                                        # if isinstance(final_str, str):
                                        #     st.text_area("Final (raw)", value=final_str or "", height=160)
                                        # else:
                                        st.json(parsed_final)
                                        # Record success
                                        self._record_workflow_history(wf_name, wf_data, user_params if top_inputs else {}, True, final_str, _start, step_results)
                                    else:
                                        st.error("Execution failed")
                                        st.text_area("Error", value=final_str or "", height=160, disabled=True)
                                        # Record failure
                                        self._record_workflow_history(wf_name, wf_data, user_params if top_inputs else {}, False, final_str, _start, step_results)

        # Build/Edit tab
        with tabs[1]:
            st.markdown("### Create or Edit Workflow")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", key="wf_name")
            with col2:
                desc = st.text_area("Description", key="wf_desc", height=70)
            #     load_existing = st.selectbox("Load existing", options=[""] + self._list_workflows(), key="wf_load")
            #     if load_existing:
            #         data = self._load_workflow(load_existing) or {}
            #         st.session_state.wf_name = data.get("name", load_existing)
            #         st.session_state.wf_desc = data.get("description", "")
            #         st.session_state.wf_steps = data.get("steps", [])
            #         st.success(f"Loaded '{load_existing}'")
            #         st.rerun()

            # Steps state
            if "wf_steps" not in st.session_state:
                st.session_state.wf_steps = []

            # Add step button
            if st.button("➕ Add Step"):
                st.session_state.wf_steps.append({"tool": "", "inputs": {}})
                st.rerun()

            # Render step editors
            if st.session_state.wf_steps:
                for i in range(len(st.session_state.wf_steps)):
                    st.markdown("---")
                    prior_defs = []
                    # Build synthetic prior tool interface for outputs listing
                    for j in range(i):
                        step_tool = st.session_state.wf_steps[j].get("tool", "")
                        cfg = all_tools.get(step_tool, {}) if step_tool else {}
                        prior_defs.append({
                            "name": step_tool,
                            "output_parameters": cfg.get("output_parameters", [])
                        })
                    self._render_step_editor(i, st.session_state.wf_steps[i], all_tools, prior_defs)
            else:
                st.info("No steps yet. Click 'Add Step'.")

            # Save
            if st.button("💾 Save Workflow", type="primary"):
                data = {
                    "name": name or st.session_state.get("wf_name"),
                    "description": desc or st.session_state.get("wf_desc", ""),
                    "steps": st.session_state.wf_steps,
                }
                if not data.get("name"):
                    st.error("Name is required")
                else:
                    if self._save_workflow(data):
                        st.success("Saved")

        # Manage tab
        with tabs[2]:
            workflows = self._list_workflows()
            if not workflows:
                st.info("No workflows saved yet.")
            else:
                for wf in workflows:
                    wf_path = self.workflows_dir / f"{wf}.json"
                    with st.expander(f"📄 {wf}", expanded=False):
                        st.code(wf_path.read_text(encoding="utf-8"), language="json")
                        colA, colB = st.columns(2)
                        with colA:
                            if st.button("🗑️ Delete", key=f"wf_del_{wf}"):
                                try:
                                    wf_path.unlink()
                                    st.success(f"Deleted {wf}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Delete failed: {e}")
                        with colB:
                            st.download_button(
                                "⬇️ Download",
                                data=wf_path.read_text(encoding="utf-8"),
                                file_name=f"{wf}.json",
                                mime="application/json",
                                key=f"wf_dl_{wf}"
                            )


