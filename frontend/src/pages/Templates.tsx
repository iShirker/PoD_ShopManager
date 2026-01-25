import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { templatesApi } from '../lib/api'
import { formatDate } from '../lib/utils'
import {
  FileText, Plus, Edit, Trash2, Loader2, X
} from 'lucide-react'

interface TemplateForm {
  name: string
  description?: string
  default_title?: string
  default_price_markup?: number
  target_platforms: string[]
}

export default function Templates() {
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(true),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TemplateForm>({
    defaultValues: {
      target_platforms: ['etsy'],
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: TemplateForm) => templatesApi.create(data),
    onSuccess: () => {
      toast.success('Template created')
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setShowCreateModal(false)
      reset()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create template')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (templateId: number) => templatesApi.delete(templateId),
    onSuccess: () => {
      toast.success('Template deleted')
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete template')
    },
  })

  const onSubmit = (data: TemplateForm) => {
    createMutation.mutate(data)
  }

  const templatesList = templates?.data?.templates || []

  return (
    <div className="space-y-6" data-testid="templates-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Listing Templates</h1>
          <p className="text-gray-500 mt-1">
            Create reusable templates for your product listings
          </p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Create Template
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : templatesList.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templatesList.map((template: any) => (
            <div key={template.id} className="card">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{template.name}</h3>
                      <p className="text-xs text-gray-500">
                        {template.products?.length || 0} products
                      </p>
                    </div>
                  </div>
                </div>

                {template.description && (
                  <p className="mt-3 text-sm text-gray-500 line-clamp-2">
                    {template.description}
                  </p>
                )}

                <div className="mt-3 flex flex-wrap gap-1">
                  {template.target_platforms?.map((platform: string) => (
                    <span
                      key={platform}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
                    >
                      {platform}
                    </span>
                  ))}
                </div>

                {template.default_price_markup > 0 && (
                  <p className="mt-2 text-xs text-gray-400">
                    Default markup: {template.default_price_markup}%
                  </p>
                )}

                <p className="mt-2 text-xs text-gray-400">
                  Created: {formatDate(template.created_at)}
                </p>

                <div className="mt-4 flex space-x-2">
                  <Link
                    to={`/templates/${template.id}`}
                    className="flex-1 btn-secondary text-sm"
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Link>
                  <button
                    onClick={() => {
                      if (confirm('Delete this template?')) {
                        deleteMutation.mutate(template.id)
                      }
                    }}
                    className="btn-secondary text-sm text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card card-body text-center py-12">
          <FileText className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No templates yet</h3>
          <p className="mt-2 text-gray-500">
            Create your first template to speed up listing creation
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 btn-primary"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Your First Template
          </button>
        </div>
      )}

      {/* Create Template Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Create Template</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  reset()
                }}
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="p-6 space-y-4">
                <div>
                  <label className="label">Template Name *</label>
                  <input
                    {...register('name', { required: 'Name is required' })}
                    type="text"
                    className="input"
                    placeholder="e.g., T-Shirt Collection"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="label">Description</label>
                  <textarea
                    {...register('description')}
                    className="input"
                    rows={2}
                    placeholder="Optional description"
                  />
                </div>

                <div>
                  <label className="label">Default Listing Title</label>
                  <input
                    {...register('default_title')}
                    type="text"
                    className="input"
                    placeholder="e.g., Custom {{product}} - {{color}}"
                  />
                </div>

                <div>
                  <label className="label">Price Markup (%)</label>
                  <input
                    {...register('default_price_markup', { valueAsNumber: true })}
                    type="number"
                    className="input"
                    placeholder="50"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Markup to add on top of supplier cost
                  </p>
                </div>

                <div>
                  <label className="label">Target Platforms</label>
                  <div className="flex space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        value="etsy"
                        {...register('target_platforms')}
                        className="mr-2"
                      />
                      Etsy
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        value="shopify"
                        {...register('target_platforms')}
                        className="mr-2"
                      />
                      Shopify
                    </label>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-gray-200 flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false)
                    reset()
                  }}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="flex-1 btn-primary"
                >
                  {createMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Create Template'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
