-- Seed data for local development

-- Create a dummy auth user (you would typically use the Supabase Studio UI for this locally)
-- Insert an Organization
INSERT INTO public.organizations (github_org_id, name, slug)
VALUES (12345678, 'Acme Corp Engineering', 'acme-corp')
ON CONFLICT DO NOTHING;

-- The rest will be populated via the App UI
