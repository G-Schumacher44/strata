# Strata Ecosystem Analysis: Looker Tooling & OAuth Strategy

## 1. The Purpose of Strata & Redundancy Check

### **The Core Purpose of Strata**
Strata is designed as a deterministic, offline-first governance and auditing framework for LookML monorepos. Its primary value is building an Intermediate Representation (IR) of the codebase to track dependency chains, identify dead code, and calculate PDT (Persistent Derived Table) costs by merging static code analysis with live Looker System Activity data.

### **Is Strata Redundant?**
**No. Strata is highly complementary to existing Looker tooling.** 

*   **Looker VS Code Extension:** The official extension focuses on *authoring*. It provides syntax highlighting, linting, bidirectional sync with the Looker server, and basic "vibe coding" (using AI to write LookML). It does not perform deep, repository-wide structural health analysis, cost audits, or dead-code elimination.
*   **Looker MCP (Google's official offering):** Google's Looker MCP exposes the *semantic layer* to AI agents. It allows an agent to ask "What was revenue last week?" and executes the corresponding semantic query to prevent raw SQL hallucinations. It is a data-querying tool.
*   **Where Strata Fits:** Strata is a **repository hygiene and governance brain**. While the official tools help you *write* LookML or *query* data, Strata helps you *refactor, clean, and govern* the LookML monorepo. The official tools lack Strata's ability to statically trace complex `extends` chains, determine the blast radius of a change, or cross-reference static views with live usage stats to flag expensive, unused PDTs.

## 2. Validating the Google OAuth Approach

You asked to validate the approach to OAuth with Google and assumed it uses a GUID.

### **The Reality of Looker & Google OAuth**
*   **Not a standard GUID:** Neither standard Looker API authentication nor Google Cloud OAuth use a traditional GUID (like `123e4567-e89b...`).
*   **Looker API3 Credentials:** Standard Looker API authentication uses a **Client ID** (a ~20-character random alphanumeric string, e.g., `AB12CD34EF56GH78IJ90`) and a Client Secret.
*   **Google OAuth (SSO / GCP-managed):** If you are relying on Google Cloud OAuth 2.0 (especially for Looker instances embedded in the Google Cloud ecosystem), it uses a **Google Cloud OAuth Client ID** (which looks like `<number-string>-<random-hash>.apps.googleusercontent.com`).
*   **Your Approach is Correct:** To pull L1 usage/cost data from Looker System Activity in a secure, read-only manner, registering an OAuth Application (or creating a dedicated Service Account / API API3 key) is the correct architectural choice. Ensure you bind this credential strictly to a `Viewer` or highly scoped custom role that only has access to the `i__looker` / System Activity models.

## 3. The "Google Perspective"

From a Google Cloud / Looker strategic perspective:
*   Google is pushing hard to make Looker the unified "semantic brain" for AI across the enterprise. 
*   However, they recognize that LookML repos in large enterprises often become bloated "spaghetti code."
*   Google strongly advocates for "LookML-as-Code" (treating BI like software engineering with CI/CD).
*   **Strata perfectly aligns with this enterprise narrative.** By providing a deterministic tool that enforces CI/CD gates, measures PDT ROI, and safely prunes dead code, Strata solves a major pain point for Google's largest customers: managing the scale and cost of massive LookML deployments.

## 4. New Tooling & Ideas to Incorporate

Here are new tools and strategies to integrate into Strata's ecosystem to maximize its value:

1.  **Looker Spectacles (Blast-Radius Optimization):**
    *   *What it is:* Spectacles runs LookML SQL validation by actually sending queries to the data warehouse to see if the underlying database schema has broken the LookML.
    *   *How Strata uses it:* Spectacles is slow and expensive to run on a whole repo. Strata's IR can determine exactly which Explores are affected by a specific View change. Strata can then trigger Spectacles in CI *only* for the affected Explores.
2.  **LAMS (LookML Actionable Management System):**
    *   *What it is:* An open-source style and linting tool for LookML.
    *   *How Strata uses it:* Incorporate LAMS output into Strata's L2 Synthesis layer. The LLM can use the deterministic LAMS style violations alongside Strata's structural IR to generate a unified "Repo Health" score.
3.  **BigQuery `INFORMATION_SCHEMA` Integration (Data Den layer):**
    *   *Idea:* If the underlying data warehouse is BigQuery, create an L1 adapter that queries BigQuery's `INFORMATION_SCHEMA.COLUMNS`. Strata can cross-reference the LookML IR dimensions directly against the live database schema to instantly flag dimensions pointing to deleted or renamed columns, completely bypassing Looker's internal validator.
4.  **Vertex AI for L2 Synthesis (Enterprise Security):**
    *   *Idea:* For enterprise deployments, rely on Google Cloud Vertex AI (using Gemini 1.5 Flash) rather than local MLX or external OpenAI models. This ensures the proprietary LookML codebase never leaves the customer's Google Cloud trust boundary, a critical selling point for adoption.
